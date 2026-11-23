#!/usr/bin/env python3
"""Keyboard GT task prompt and schema helpers."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from agent.current_focus_marker import install_current_focus_marker
from agent.evidence_assisted_observation import append_evidence_pack_prompt, install_evidence_assisted_observation, load_evidence_pack_manifest
from agent.gt.path_utils import safe_copy2, safe_mkdir, safe_unlink, windows_long_path, write_json_file, write_text_file

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError('PyYAML is required to load Keyboard GT task YAML files.') from exc


IssueFamily = Literal[
    'keyboard_nonreachable',
    'keyboard_trap',
    'character_key_shortcuts',
    'on_focus',
    'on_input',
]
SUPPORTED_ISSUE_TYPES = {'keyboard_nonreachable', 'on_input', 'character_key_shortcuts'}
LEVEL3_ISSUE_FAMILY = 'keyboard_assessment_1_1_1_2_1_3_1_4_1_6'
ISSUE_TYPE_VALUES = [
    'keyboard_nonreachable',
    'keyboard_trap',
    'character_key_shortcuts',
    'on_focus',
    'on_input',
]
GT_KEYBOARD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_KEYBOARD_DIR.parent.parent
BROWSER_USE_ROOT = PROJECT_ROOT.parent / 'browser-use'
TASKS_DIR = GT_KEYBOARD_DIR / 'tasks'
EVALUATE_RULES_DIR = GT_KEYBOARD_DIR / 'evaluate-rules'
RUNS_DIR = GT_KEYBOARD_DIR / 'runs'
CONVERSATION_CACHE_DIR = PROJECT_ROOT / 'agent' / '.conv'
BROWSER_RUNTIME_AUTH_DIR = GT_KEYBOARD_DIR / 'auth' / 'browser_runtime'
PASS_L1_PATCH_MANIFEST = GT_KEYBOARD_DIR / 'runtime_patches' / 'pass_l1_counterfactual.yaml'
PROMPT_TEMPLATE_ID = 'keyboard_compact_no_assessment_requirement_v2_20260615'

if str(BROWSER_USE_ROOT) not in sys.path:
    sys.path.insert(0, str(BROWSER_USE_ROOT))

KEYBOARD_REACHABILITY_RULE = (
    'the specified target or control cannot be reached by keyboard navigation, cannot be operated with its expected keyboard interaction once reached, or disrupts the expected keyboard path for reaching downstream controls'
)
WCAG_REFERENCE_PREFIX = 'WCAG reference: '
ON_INPUT_RULE = (
    'changing the target control value or selection automatically causes a change of context without prior user advice and without a separate confirmation step'
)
CHARACTER_KEY_RULE = (
    'a single printable-character shortcut is active when focus is outside an editable target, and the shortcut cannot be turned off, remapped, or limited to focus on the target'
)
KEYBOARD_TRAP_RULE = (
    'keyboard focus can move into the target component or region but cannot move away using only expected keyboard interaction, or the page does not advise the required nonstandard exit method'
)
ON_FOCUS_RULE = (
    'the target component receives focus and initiates a change of context without prior user advice and without explicit activation'
)
KEYBOARD_EVIDENCE_CONTRACT = (
    'Verify keyboard behavior by navigating to and operating the same target or control through observed Tab, Shift+Tab, arrow-key, Enter, Space, Escape, or character-key interaction as relevant. '
    'Pointer interaction may be used only to reveal or cross-check the target, not as proof that the target or control itself is keyboard reachable or operable. '
    'Do not rely on source-code inspection alone.'
)
CHARACTER_KEY_EVIDENCE_CONTRACT = (
    'Verify the shortcut by placing focus outside editable targets and outside the relevant component, pressing the single printable character, and checking whether the shortcut fires without an available off, remap, or focus-only mechanism. '
    'Pointer interaction may be used only to reveal or cross-check the target or settings, not as proof that the shortcut is compliant. '
    'Do not rely on source-code inspection alone.'
)


class VerificationOutput(BaseModel):
    verdict: Literal['issue_found', 'no_issue_found']
    selector: str
    target: str
    issue_type: IssueFamily
    observed_behavior: str
    evidence: str


class IssueOutput(BaseModel):
    selector: str
    target: str
    issue_type: IssueFamily
    observed_behavior: str
    evidence: str


class MultiIssueVerificationOutput(BaseModel):
    verdict: Literal['issue_found', 'no_issue_found']
    issues: list[IssueOutput]


@dataclass
class TaskConfig:
    task_id: str
    instance_id: str
    start_url: str
    wcag_target: str
    wcag_clause_text: str
    target_description: str
    issue_family: str
    target_selector: str | None = None
    task_type: str = 'verification'
    evaluate_rule_file: str | None = None
    difficulty: str | None = None
    issue_domain: str | None = None
    modality_policy: str | None = None
    auth_state_file: str | None = None
    wcag_source_url: str | None = None
    wcag_criteria: dict[str, dict[str, str]] | None = None
    ai_web: dict[str, Any] | None = None
    setup: str | None = None
    output_format: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> 'TaskConfig':
        return cls(**data)


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('YAML root must be a mapping: ' + str(path))
    return data


def load_task(path: Path) -> TaskConfig:
    return TaskConfig.from_mapping(load_yaml(path))


def _clean_text(value: str) -> str:
    return ' '.join(str(value).split())


def _sentence(value: str) -> str:
    value = _clean_text(value)
    if value.endswith(('.', '?', '!')):
        return value
    return value + '.'


def _is_level_2(task: TaskConfig) -> bool:
    return task.difficulty == 'level_2_clause_given_location_hidden' or task.task_id.endswith('.level2.v1')


def _is_level_3(task: TaskConfig) -> bool:
    return task.issue_family == LEVEL3_ISSUE_FAMILY or task.task_id.endswith('.level3.v1')


def is_multi_issue_task(task: TaskConfig) -> bool:
    return isinstance(task.output_format.get('issues'), list) or _is_level_2(task) or _is_level_3(task)


def _output_contract(task: TaskConfig) -> str:
    if is_multi_issue_task(task):
        return 'Report only issues that are present. If no issues are present, use verdict `no_issue_found` and leave the `issues` list empty.'
    return 'If the issue is present, use verdict `issue_found`; otherwise use verdict `no_issue_found`.'


def _issue_label(family: str) -> str:
    if family == 'keyboard_nonreachable':
        return 'WCAG 2.1.1 keyboard reachability issue'
    if family == 'on_input':
        return 'WCAG 3.2.2 on-input context-change issue'
    if family == 'character_key_shortcuts':
        return 'WCAG 2.1.4 character-key-shortcut issue'
    raise ValueError('Unsupported Keyboard issue_family: ' + family)


def _family_rule(family: str) -> str:
    if family == 'keyboard_nonreachable':
        return KEYBOARD_REACHABILITY_RULE
    if family == 'on_input':
        return ON_INPUT_RULE
    if family == 'character_key_shortcuts':
        return CHARACTER_KEY_RULE
    raise ValueError('Unsupported Keyboard issue_family: ' + family)


def _assessment_name(family: str) -> str:
    if family == 'keyboard_nonreachable':
        return 'Accessibility Insights Keyboard navigation'
    if family == 'on_input':
        return 'Accessibility Insights On input'
    if family == 'character_key_shortcuts':
        return 'Accessibility Insights Character key shortcuts'
    raise ValueError('Unsupported Keyboard issue_family: ' + family)


def _evidence_contract(family: str) -> str:
    if family == 'keyboard_nonreachable':
        return KEYBOARD_EVIDENCE_CONTRACT
    if family == 'on_input':
        return KEYBOARD_EVIDENCE_CONTRACT
    if family == 'character_key_shortcuts':
        return CHARACTER_KEY_EVIDENCE_CONTRACT
    raise ValueError('Unsupported Keyboard issue_family: ' + family)


def build_task_prompt(task: TaskConfig) -> str:
    if _is_level_3(task):
        return build_level3_prompt(task)
    if _is_level_2(task):
        return build_level2_prompt(task)
    if task.issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Keyboard issue_family: ' + task.issue_family)
    if not task.target_selector:
        raise ValueError('Keyboard BASE L1 tasks require target_selector: ' + task.task_id)

    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + ' for ' + _assessment_name(task.issue_family) + '.',
        'Target selector: `' + _clean_text(task.target_selector) + '`',
        WCAG_REFERENCE_PREFIX + _clean_text(task.wcag_target) + ' - ' + _clean_text(task.wcag_clause_text),
    ]
    if task.setup:
        chunks.append(_sentence(task.setup))
    chunks.append('Report a ' + _issue_label(task.issue_family) + ' only if ' + _sentence(_family_rule(task.issue_family)))
    chunks.append(_evidence_contract(task.issue_family))
    chunks.append(_output_contract(task))
    return '\n\n'.join(chunks)


def build_level2_prompt(task: TaskConfig) -> str:
    if task.issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Keyboard issue_family: ' + task.issue_family)
    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + ' for ' + _assessment_name(task.issue_family) + '.',
        WCAG_REFERENCE_PREFIX + _clean_text(task.wcag_target) + ' - ' + _clean_text(task.wcag_clause_text),
    ]
    if task.setup:
        chunks.append(_sentence(task.setup))
    chunks.append('Report a ' + _issue_label(task.issue_family) + ' for each target where ' + _sentence(_family_rule(task.issue_family)))
    chunks.append(_evidence_contract(task.issue_family))
    chunks.append(_output_contract(task))
    return '\n\n'.join(chunks)


def build_level3_prompt(task: TaskConfig) -> str:
    if not task.wcag_criteria:
        raise ValueError('Level 3 Keyboard tasks require wcag_criteria')
    criteria_lines = ['WCAG criteria:']
    for label, criterion in task.wcag_criteria.items():
        criteria_lines.append(label + ' -> ' + _clean_text(criterion['target']) + ': ' + _clean_text(criterion['text']))
    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + '.',
        '\n'.join(criteria_lines),
    ]
    if task.setup:
        chunks.append(_sentence(task.setup))
    chunks.append(
        'Report an issue for each keyboard target or interaction where either 1.1 applies: '
        + KEYBOARD_REACHABILITY_RULE
        + '; or 1.2 applies: '
        + KEYBOARD_TRAP_RULE
        + '; or 1.3 applies: '
        + ON_FOCUS_RULE
        + '; or 1.4 applies: '
        + ON_INPUT_RULE
        + '; or 1.6 applies: '
        + CHARACTER_KEY_RULE
        + '.'
    )
    chunks.append(KEYBOARD_EVIDENCE_CONTRACT)
    chunks.append(_output_contract(task))
    return '\n\n'.join(chunks)


def _issue_output_format(output_format: dict[str, Any], multi: bool) -> dict[str, Any]:
    if multi:
        issues = output_format.get('issues')
        if isinstance(issues, list) and issues and isinstance(issues[0], dict):
            return issues[0]
        raise ValueError('Keyboard output_format.issues[0] must be present and must be a mapping.')
    return output_format


def _field_description(output_format: dict[str, Any], field_name: str) -> str:
    value = output_format.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError('Keyboard output_format.' + field_name + ' must be a non-empty string.')


def multi_output_model_schema(output_format: dict[str, Any] | None = None) -> type[BaseModel]:
    if output_format is None:
        raise ValueError('Keyboard output_format is required to build the output schema.')
    issue_format = _issue_output_format(output_format, multi=True)
    issue_model = create_model(
        'KeyboardIssueOutput',
        selector=(str, Field(..., description=_field_description(issue_format, 'selector'))),
        target=(str, Field(..., description=_field_description(issue_format, 'target'))),
        issue_type=(IssueFamily, Field(..., description=_field_description(issue_format, 'issue_type'))),
        observed_behavior=(str, Field(..., description=_field_description(issue_format, 'observed_behavior'))),
        evidence=(str, Field(..., description=_field_description(issue_format, 'evidence'))),
    )
    return create_model(
        'MultiIssueVerificationOutput',
        verdict=(Literal['issue_found', 'no_issue_found'], Field(..., description=_field_description(output_format, 'verdict'))),
        issues=(list[issue_model], ...),
    )


def fixed_output_model_schema_for_family(issue_family: str, output_format: dict[str, Any] | None = None, *, multi: bool = False) -> type[BaseModel]:
    if issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Keyboard issue_family: ' + issue_family)
    if output_format is None:
        raise ValueError('Keyboard output_format is required to build the output schema.')
    issue_format = _issue_output_format(output_format, multi=multi)
    issue_model = create_model(
        'IssueOutput_' + issue_family,
        selector=(str, Field(..., description=_field_description(issue_format, 'selector'))),
        target=(str, Field(..., description=_field_description(issue_format, 'target'))),
        issue_type=(Literal[issue_family], Field(..., description=_field_description(issue_format, 'issue_type'))),
        observed_behavior=(str, Field(..., description=_field_description(issue_format, 'observed_behavior'))),
        evidence=(str, Field(..., description=_field_description(issue_format, 'evidence'))),
    )
    if multi:
        return create_model(
            'MultiIssueVerificationOutput_' + issue_family,
            verdict=(Literal['issue_found', 'no_issue_found'], Field(..., description=_field_description(output_format, 'verdict'))),
            issues=(list[issue_model], ...),
        )
    return create_model(
        'VerificationOutput_' + issue_family,
        verdict=(Literal['issue_found', 'no_issue_found'], Field(..., description=_field_description(output_format, 'verdict'))),
        selector=(str, Field(..., description=_field_description(output_format, 'selector'))),
        target=(str, Field(..., description=_field_description(output_format, 'target'))),
        issue_type=(Literal[issue_family], Field(..., description=_field_description(output_format, 'issue_type'))),
        observed_behavior=(str, Field(..., description=_field_description(output_format, 'observed_behavior'))),
        evidence=(str, Field(..., description=_field_description(output_format, 'evidence'))),
    )


def output_model_schema_for_task(task: TaskConfig) -> type[BaseModel]:
    if not _is_level_3(task) and task.issue_family in SUPPORTED_ISSUE_TYPES:
        return fixed_output_model_schema_for_family(task.issue_family, task.output_format, multi=is_multi_issue_task(task))
    if is_multi_issue_task(task):
        return multi_output_model_schema(task.output_format)
    return VerificationOutput


def resolve_task_path(task_arg: str) -> Path:
    candidate = Path(task_arg)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    return TASKS_DIR / task_arg


def resolve_optional_path(path_str: str | None) -> Path | None:
    if not path_str:
        return None
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def resolve_runs_root(path_str: str | None) -> Path:
    if not path_str:
        return RUNS_DIR
    path = Path(path_str)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def build_conversation_dir(run_dir: Path) -> Path:
    if os.name != 'nt':
        return run_dir / 'conversation'
    token = hashlib.sha1(str(run_dir).encode('utf-8')).hexdigest()[:16]
    return CONVERSATION_CACHE_DIR / token


def build_task_output_dir_name(task_id: str) -> str:
    if os.name != 'nt':
        return task_id
    parts = task_id.split('.')
    prefix = '.'.join(parts[:3]) if len(parts) >= 3 else task_id[:24]
    if len(prefix) > 40 and len(parts) >= 2:
        prefix = '.'.join(parts[:2])
    if len(prefix) > 40:
        prefix = prefix[:40]
    if task_id.endswith('.verify.level3.v1'):
        variant = 'verify_l3_v1'
    elif task_id.endswith('.verify.level2.v1'):
        variant = 'verify_l2_v1'
    elif task_id.endswith('.verify.v1'):
        variant = 'verify_v1'
    else:
        variant = '_'.join(parts[-3:]).replace('level', 'l')
    digest = hashlib.sha1(task_id.encode('utf-8')).hexdigest()[:8]
    return f'{prefix}.{variant}.{digest}'


def observation_condition_name(*, current_focus_marker: bool, evidence_pack_enabled: bool) -> str:
    parts = []
    if current_focus_marker:
        parts.append('current_focus_marker_v1')
    if evidence_pack_enabled:
        parts.append('evidence_pack_v1')
    return '+'.join(parts) if parts else 'baseline'


def resolve_evaluate_rule(task_path: Path, task: TaskConfig) -> Path | None:
    explicit = resolve_optional_path(task.evaluate_rule_file)
    if explicit is not None and explicit.exists():
        return explicit
    by_name = EVALUATE_RULES_DIR / task_path.name
    if by_name.exists():
        return by_name
    by_task_id = EVALUATE_RULES_DIR / f'{task.task_id}.yaml'
    if by_task_id.exists():
        return by_task_id
    return None


def write_json(path: Path, payload: Any) -> None:
    write_json_file(path, payload)


def write_text(path: Path, text: str) -> None:
    write_text_file(path, text)


def save_history_json(history: Any, path: Path) -> None:
    try:
        history.save_to_file(windows_long_path(path))
    except UnicodeEncodeError:
        data = history.model_dump() if hasattr(history, 'model_dump') else history.dict()
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        safe_mkdir(path.parent)
        with open(windows_long_path(path), 'wb') as handle:
            handle.write(payload.encode('utf-8', errors='replace'))


def load_storage_state(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Auth state file is not valid UTF-8 JSON: ' + str(path)) from exc
    if not isinstance(payload, dict):
        raise ValueError('Auth state file must contain a JSON object: ' + str(path))
    return payload


def create_runtime_storage_state_file(storage_state: dict[str, Any] | None, run_dir: Path) -> Path | None:
    if storage_state is None:
        return None
    token = hashlib.sha1(str(run_dir.resolve(strict=False)).encode('utf-8')).hexdigest()[:16]
    runtime_dir = BROWSER_RUNTIME_AUTH_DIR / token
    safe_mkdir(runtime_dir)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', prefix='state_', dir=windows_long_path(runtime_dir), delete=False) as handle:
        json.dump(storage_state, handle, ensure_ascii=True, indent=2)
        handle.write('\n')
        return Path(handle.name)


def cleanup_runtime_storage_state_file(path: Path | None) -> None:
    if path is None:
        return
    safe_unlink(path)


def build_usage_payload(history: Any) -> dict[str, Any]:
    usage = getattr(history, 'usage', None)
    if usage is None:
        return {
            'usage_missing': True,
            'prompt_tokens': None,
            'prompt_cached_tokens': None,
            'prompt_cache_creation_tokens': None,
            'prompt_image_tokens': None,
            'completion_tokens': None,
            'reasoning_tokens': None,
            'total_tokens': None,
            'estimated_cost_usd': None,
            'raw_usage': None,
        }
    raw_usage = usage.model_dump() if hasattr(usage, 'model_dump') else dict(usage)
    return {
        'usage_missing': False,
        'prompt_tokens': raw_usage.get('total_prompt_tokens'),
        'prompt_cached_tokens': raw_usage.get('total_prompt_cached_tokens'),
        'prompt_cache_creation_tokens': raw_usage.get('total_prompt_cache_creation_tokens'),
        'prompt_image_tokens': raw_usage.get('total_prompt_image_tokens'),
        'completion_tokens': raw_usage.get('total_completion_tokens'),
        'reasoning_tokens': raw_usage.get('total_reasoning_tokens'),
        'total_tokens': raw_usage.get('total_tokens'),
        'estimated_cost_usd': raw_usage.get('total_cost'),
        'raw_usage': raw_usage,
    }


def build_review_template(task: TaskConfig, evaluate_rule_path: Path | None) -> str:
    lines = [
        '# Manual Review: ' + task.task_id,
        '',
        '- instance_id: ' + task.instance_id,
        '- wcag_target: ' + task.wcag_target,
        '- evaluate_rule: ' + (str(evaluate_rule_path) if evaluate_rule_path else 'N/A'),
        '',
        '## Review',
        '- verdict_correct: ',
        '- target_correct: ',
        '- behavior_correct: ',
        '- overall: ',
        '',
        '## Notes',
        '- ',
    ]
    return '\n'.join(lines)


def get_browser_use_classes():
    if str(BROWSER_USE_ROOT) not in sys.path:
        sys.path.insert(0, str(BROWSER_USE_ROOT))
    from browser_use import Agent, BrowserSession

    return Agent, BrowserSession


def create_task_llm(model: str, temperature: float, salvage_multi_json: bool, reasoning_effort: str | None = None):
    from agent.llm_setup import create_llm

    return create_llm(
        model=model,
        temperature=temperature,
        salvage_multi_json=salvage_multi_json,
        reasoning_effort=reasoning_effort,
    )


def infer_site_from_task(task: TaskConfig, site_override: str | None = None) -> str | None:
    if site_override:
        return site_override
    for value in (task.instance_id, task.task_id):
        if value and '.' in value:
            return value.split('.', 1)[0]
    return None


async def refresh_task_auth_state(site: str, output_path: Path, headless: bool = True) -> Path:
    from agent.gt.save_storage_state import create_storage_state

    await create_storage_state(site, output_path, headed=not headless)
    return output_path


async def probe_task_auth_state(site: str, storage_state_path: Path) -> tuple[bool, str]:
    from agent.gt.probe_auth import probe

    return await probe(site, storage_state_path)


async def cleanup_browser_session(browser_session: Any | None) -> None:
    if browser_session is None:
        return
    try:
        await browser_session.kill()
    except Exception:
        pass


def load_pass_l1_patch_manifest() -> dict[str, Any]:
    if not PASS_L1_PATCH_MANIFEST.exists():
        return {}
    manifest = load_yaml(PASS_L1_PATCH_MANIFEST)
    patches = manifest.get('patches') or {}
    if not isinstance(patches, dict):
        raise ValueError('patches must be a mapping: ' + str(PASS_L1_PATCH_MANIFEST))
    return patches


def is_generated_pass_task(task_path: Path, task: TaskConfig) -> bool:
    joined = '/'.join(part.lower() for part in task_path.parts)
    if 'generated_pass' in joined:
        return True
    return bool(task.evaluate_rule_file and 'generated_pass' in task.evaluate_rule_file.lower())


def pass_l1_patch_for_task(task_path: Path, task: TaskConfig) -> dict[str, Any] | None:
    if not is_generated_pass_task(task_path, task):
        return None
    patches = load_pass_l1_patch_manifest()
    patch = patches.get(task.instance_id)
    if patch is None:
        raise ValueError('Missing Keyboard PASS L1 runtime patch for ' + task.instance_id + ': ' + str(PASS_L1_PATCH_MANIFEST))
    if not isinstance(patch, dict):
        raise ValueError('Keyboard PASS L1 runtime patch must be a mapping for ' + task.instance_id)
    return patch


PASS_L1_PATCH_JS = r'''
(() => {
  const ID = __ID__;
  const SPEC = __SPEC__;
  const TASK_SELECTOR = __TARGET__;
  const flags = {
    activation: new WeakSet(),
    magentoGridForcedHidden: new WeakSet(),
    magentoGridMenuItem: new WeakSet(),
    magentoGridButton: new WeakSet(),
    filteredSearchToken: new WeakSet(),
    pendingSelect: new WeakSet(),
    pendingActivation: new WeakSet(),
    pendingActivationBypass: new WeakSet(),
    gitlabSortButton: new WeakSet(),
    gitlabSortItem: new WeakSet(),
    sidebarToggle: new WeakSet(),
    chartLegend: new WeakSet(),
    redditSortButton: new WeakSet(),
    redditSortItem: new WeakSet(),
    editorEscape: new WeakSet(),
    jqueryDatepickerItem: new WeakSet(),
    gitlabModalDropdown: new WeakSet(),
    gl15Nav: new WeakSet(),
    gl15Calendar: new WeakSet(),
    gl82Nav: new WeakSet(),
    gl82Calendar: new WeakSet(),
    gl82Root: new WeakSet(),
  };
  const refs = {
    sidebarLabelByToggle: new WeakMap(),
  };
  const patchLog = [];
  let filteredSearchTokenObserver = null;
  let filteredSearchTokenObserverTimer = null;
  let magentoGridActionsDocumentEscapeInstalled = false;
  let shortcutScopeInstalled = false;
  let jqueryDatepickerState = null;
  let jqueryDatepickerRefresh = null;
  let jqueryDatepickerHidePatched = false;
  let gitlabPikaSingleState = null;
  let gitlabPikaRangeState = null;
  let lastInstallResult = null;
  let lastInstallError = null;
  const log = (event, detail = {}) => {
    patchLog.push({id: ID, kind: SPEC.kind, event, detail, time: Date.now()});
    if (patchLog.length > 160) patchLog.splice(0, patchLog.length - 160);
  };
  const nodes = (selector) => {
    try { return Array.from(document.querySelectorAll(selector || '')); }
    catch (error) { log('selector_error', {selector, message: String(error && error.message || error)}); return []; }
  };
  const visible = (el) => {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
  };
  const selector = SPEC.selector || TASK_SELECTOR;
  const targetNodes = () => nodes(selector).filter(visible);
  const isActivationKey = (event) => event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar';
  const dispatchMouseActivation = (el) => {
    for (const type of ['mousedown', 'mouseup', 'click']) {
      el.dispatchEvent(new MouseEvent(type, {bubbles: true, cancelable: true, view: window}));
    }
  };
  const makeFocusable = (el) => {
    el.setAttribute('tabindex', '0');
    el.removeAttribute('disabled');
    el.setAttribute('aria-disabled', 'false');
  };

  const installMakeFocusable = (clickable) => {
    const items = targetNodes();
    items.forEach((el) => {
      makeFocusable(el);
      if (clickable && !el.getAttribute('role') && !['a', 'button', 'input', 'select', 'textarea'].includes(el.tagName.toLowerCase())) {
        el.setAttribute('role', 'button');
      }
      if (clickable && !flags.activation.has(el)) {
        el.addEventListener('keydown', (event) => {
          if (!isActivationKey(event)) return;
          event.preventDefault();
          event.stopPropagation();
          el.click();
          log('keyboard_activate_click', {tag: el.tagName, text: (el.innerText || el.textContent || '').trim().slice(0, 80)});
        }, true);
        flags.activation.add(el);
      }
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installMagentoGridActionsMenuRepair = () => {
    const header = () => document.querySelector('.admin__data-grid-header') || document;
    const itemNodes = () => targetNodes();
    const allItemNodes = () => nodes(selector);
    const itemText = (el) => (el && (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ')) || '';
    const isMenuItem = (el) => !!(el && el.closest && el.closest('.admin__data-grid-header') && (el.matches(selector) || (el.closest(selector) && el.closest(selector).matches(selector))));
    const menuFor = (el) => el && el.closest && (el.closest('ul, ol, [role=menu], .admin__action-dropdown-menu, .action-menu') || el.closest('.admin__data-grid-action-select-wrap, .action-select-wrap, .admin__action-dropdown-wrap'));
    const wrapFor = (el) => el && el.closest && (el.closest('.admin__data-grid-action-select-wrap, .action-select-wrap, .admin__action-dropdown-wrap') || el.closest('.admin__data-grid-header'));
    const actionButtons = () => {
      const root = header();
      const candidates = Array.from(root.querySelectorAll('button, .action-select'));
      return candidates.filter((button) => {
        const text = itemText(button);
        const title = button.getAttribute('title') || button.getAttribute('aria-label') || '';
        return visible(button) && (button.classList.contains('action-select') || /\bActions\b/i.test(text) || /\bActions\b/i.test(title));
      });
    };
    const actionButtonFor = (source) => {
      const wrap = wrapFor(source);
      const local = wrap ? Array.from(wrap.querySelectorAll('button, .action-select')).find((button) => visible(button) && (button.classList.contains('action-select') || /\bActions\b/i.test(itemText(button)) || /\bActions\b/i.test(button.getAttribute('title') || ''))) : null;
      return local || actionButtons()[0] || null;
    };
    const menuContainers = (source) => {
      const result = new Set();
      const add = (el) => { if (el) result.add(el); };
      add(menuFor(source));
      add(wrapFor(source));
      allItemNodes().forEach((item) => { add(menuFor(item)); add(wrapFor(item)); });
      return Array.from(result).filter((el) => el && el !== document && el !== document.documentElement && el !== document.body);
    };
    const clearForcedHidden = (source) => {
      menuContainers(source).forEach((el) => {
        if (flags.magentoGridForcedHidden.has(el)) {
          el.style.removeProperty('display');
          el.removeAttribute('aria-hidden');
          flags.magentoGridForcedHidden.delete(el);
        }
      });
    };
    const forceClosed = (source) => {
      menuContainers(source).forEach((el) => {
        el.classList.remove('_active', 'active', 'open', 'show');
        if (el.matches('ul, ol, [role=menu], .admin__action-dropdown-menu, .action-menu')) {
          el.style.setProperty('display', 'none', 'important');
          el.setAttribute('aria-hidden', 'true');
          flags.magentoGridForcedHidden.add(el);
        }
      });
    };
    const focusButton = (button) => {
      if (!button) return false;
      try { button.focus({preventScroll: false}); } catch (_) { button.focus(); }
      return document.activeElement === button;
    };
    const closeMenu = (source, focus = true) => {
      const button = actionButtonFor(source);
      const hadVisibleItems = itemNodes().length > 0;
      if (button) button.setAttribute('aria-expanded', 'false');
      if (button && hadVisibleItems) dispatchMouseActivation(button);
      setTimeout(() => {
        if (itemNodes().length > 0) forceClosed(source);
        if (button) button.setAttribute('aria-expanded', 'false');
        if (focus) focusButton(button);
        log('magento_grid_actions_menu_close', {hadVisibleItems, focusedButton: !!focus});
      }, 0);
      setTimeout(() => {
        if (itemNodes().length > 0) forceClosed(source);
        if (button) button.setAttribute('aria-expanded', 'false');
        if (focus) focusButton(button);
      }, 80);
      return true;
    };
    const focusItem = (items, index) => {
      if (!items.length) return false;
      const next = items[((index % items.length) + items.length) % items.length];
      clearForcedHidden(next);
      makeFocusable(next);
      try { next.focus({preventScroll: false}); } catch (_) { next.focus(); }
      return document.activeElement === next;
    };
    const moveFocus = (item, delta) => {
      const items = itemNodes();
      const index = Math.max(0, items.indexOf(item));
      const ok = focusItem(items, index + delta);
      log('magento_grid_actions_menu_roving_focus', {delta, ok, count: items.length});
      return ok;
    };
    const openAndFocus = (button, index) => {
      clearForcedHidden(button);
      const focusVisibleItem = () => {
        const items = itemNodes();
        if (items.length) focusItem(items, index < 0 ? items.length - 1 : index);
      };
      if (itemNodes().length) {
        repairItems();
        focusVisibleItem();
        return true;
      }
      dispatchMouseActivation(button);
      setTimeout(() => { repairItems(); focusVisibleItem(); }, 0);
      setTimeout(() => { repairItems(); focusVisibleItem(); }, 80);
      return true;
    };
    function repairItems() {
      const items = itemNodes();
      items.forEach((item) => {
        makeFocusable(item);
        if (!item.getAttribute('role')) item.setAttribute('role', 'menuitem');
        if (flags.magentoGridMenuItem.has(item)) return;
        item.addEventListener('keydown', (event) => {
          if (event.key === 'Escape') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            closeMenu(item, true);
          } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            moveFocus(item, 1);
          } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            moveFocus(item, -1);
          } else if (event.key === 'Home') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            focusItem(itemNodes(), 0);
          } else if (event.key === 'End') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            const items = itemNodes();
            focusItem(items, items.length - 1);
          } else if (isActivationKey(event)) {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            dispatchMouseActivation(item);
            log('magento_grid_actions_menu_item_activate', {text: itemText(item).slice(0, 100)});
            setTimeout(() => closeMenu(item, true), 0);
          }
        }, true);
        item.addEventListener('focusin', () => { clearForcedHidden(item); }, true);
        flags.magentoGridMenuItem.add(item);
      });
      return items;
    }
    const repairButtons = () => {
      const buttons = actionButtons();
      buttons.forEach((button) => {
        makeFocusable(button);
        if (flags.magentoGridButton.has(button)) return;
        button.addEventListener('click', () => {
          clearForcedHidden(button);
          setTimeout(repairItems, 0);
          setTimeout(repairItems, 80);
        }, true);
        button.addEventListener('keydown', (event) => {
          if (event.key === 'Escape') {
            if (!itemNodes().length) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            closeMenu(button, true);
          } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            openAndFocus(button, 0);
          } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            openAndFocus(button, -1);
          } else if (isActivationKey(event)) {
            clearForcedHidden(button);
            setTimeout(() => { repairItems(); const items = itemNodes(); if (items.length) focusItem(items, 0); }, 80);
            setTimeout(() => { repairItems(); const items = itemNodes(); if (items.length) focusItem(items, 0); }, 160);
          }
        }, true);
        flags.magentoGridButton.add(button);
      });
      return buttons;
    };
    const installDocumentEscape = () => {
      if (magentoGridActionsDocumentEscapeInstalled) return;
      document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const target = event.target;
        if (!target || !target.closest || !target.closest('.admin__data-grid-header')) return;
        if (!itemNodes().length) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        closeMenu(target, true);
      }, true);
      magentoGridActionsDocumentEscapeInstalled = true;
    };
    const items = repairItems();
    const buttons = repairButtons();
    installDocumentEscape();
    return {installed: items.length > 0 || buttons.length > 0, count: items.length, buttonCount: buttons.length};
  };

  const installGitlabFilteredSearchTokenRepair = () => {
    const removeSelectors = [
      '.remove-token',
      '.js-remove-token',
      '[aria-label*="remove" i]',
      '[title*="remove" i]',
      '[data-testid*="remove" i]',
    ];
    const repairToken = (token, index) => {
      makeFocusable(token);
      if (!token.getAttribute('role')) token.setAttribute('role', 'button');
      const selectable = token.querySelector('.selectable[role="button"], .selectable') || token;
      const remove = removeSelectors.map((sel) => token.querySelector(sel)).find(Boolean);
      const tokenText = (token.innerText || token.textContent || '').trim().replace(/\s+/g, ' ');
      const label = tokenText ? 'Filtered search token: ' + tokenText : 'Filtered search token';
      if (!token.getAttribute('aria-label')) token.setAttribute('aria-label', label);
      if (selectable && selectable !== token) {
        makeFocusable(selectable);
        if (!selectable.getAttribute('role')) selectable.setAttribute('role', 'button');
        if (!selectable.getAttribute('aria-label')) selectable.setAttribute('aria-label', label);
      }
      if (remove) {
        makeFocusable(remove);
        if (!remove.getAttribute('role')) remove.setAttribute('role', 'button');
        if (!remove.getAttribute('aria-label')) remove.setAttribute('aria-label', 'Remove ' + label.replace(/^Filtered search token:\s*/i, 'filtered search token '));
      }
      const activateSelectable = () => {
        const target = selectable || token;
        dispatchMouseActivation(target);
        log('filtered_search_token_activate', {index, text: tokenText.slice(0, 100)});
      };
      const activateRemove = () => {
        if (!remove) return false;
        dispatchMouseActivation(remove);
        log('filtered_search_token_remove', {index, text: tokenText.slice(0, 100)});
        return true;
      };
      const bind = (el, name) => {
        if (!el || flags.filteredSearchToken.has(el)) return;
        el.addEventListener('keydown', (event) => {
          const onRemove = remove && (event.target === remove || (remove.contains && remove.contains(event.target)));
          if (event.key === 'Delete' || event.key === 'Backspace') {
            if (!remove) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            activateRemove();
          } else if (isActivationKey(event)) {
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            if (name === 'remove' || onRemove) activateRemove();
            else activateSelectable();
          }
        }, true);
        el.addEventListener('focusin', () => {
          try { el.scrollIntoView({block: 'center', inline: 'nearest'}); } catch (_) {}
        }, true);
        flags.filteredSearchToken.add(el);
      };
      bind(token, 'token');
      if (selectable && selectable !== token) bind(selectable, 'selectable');
      if (remove) bind(remove, 'remove');
      return {hasRemove: !!remove, hasSelectable: !!selectable};
    };
    const applyRepair = () => {
      const tokens = targetNodes();
      const details = tokens.map(repairToken);
      return {tokens, details};
    };
    const result = applyRepair();
    if (!filteredSearchTokenObserver) {
      const observer = new MutationObserver(() => {
        clearTimeout(filteredSearchTokenObserverTimer);
        filteredSearchTokenObserverTimer = setTimeout(applyRepair, 0);
      });
      observer.observe(document.documentElement, {childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'tabindex', 'role', 'aria-label']});
      filteredSearchTokenObserver = observer;
    }
    return {installed: result.tokens.length > 0, count: result.tokens.length, details: result.details};
  };

  const installNativeSelectPendingApply = () => {
    const items = targetNodes();
    items.forEach((el, index) => {
      if (flags.pendingSelect.has(el)) return;
      const originalOnchangeAttr = el.getAttribute('onchange');
      const originalOnchange = el.onchange;
      el.removeAttribute('onchange');
      el.onchange = null;
      const state = {pendingValue: el.value, pendingUrl: null};
      const blockChange = (event) => {
        const option = el.options && el.options[el.selectedIndex];
        state.pendingValue = el.value;
        state.pendingUrl = option ? option.value : el.value;
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        log('select_change_pending', {index, value: state.pendingValue});
      };
      el.addEventListener('change', blockChange, true);
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = SPEC.apply_label || 'Apply';
      button.style.marginLeft = '8px';
      button.addEventListener('click', () => {
        const option = el.options && el.options[el.selectedIndex];
        const destination = option ? option.value : el.value;
        if (destination && /^https?:\/\//.test(destination)) window.location.href = destination;
        else if (destination && destination.startsWith('/')) window.location.href = destination;
        else if (typeof originalOnchange === 'function') originalOnchange.call(el, new Event('change'));
        else if (originalOnchangeAttr) Function(originalOnchangeAttr).call(el);
      });
      el.insertAdjacentElement('afterend', button);
      flags.pendingSelect.add(el);
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installActivationPendingApply = () => {
    const items = targetNodes();
    items.forEach((el, index) => {
      if (flags.pendingActivation.has(el)) return;
      if (!el.hasAttribute('tabindex') && !['button', 'a', 'input', 'select', 'textarea'].includes(el.tagName.toLowerCase())) el.setAttribute('tabindex', '0');
      const stop = (event) => {
        if (flags.pendingActivationBypass.has(el)) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        log('activation_pending', {index});
      };
      el.addEventListener('click', stop, true);
      el.addEventListener('keydown', (event) => { if (isActivationKey(event) || event.key === 'ArrowDown') stop(event); }, true);
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = SPEC.apply_label || 'Apply';
      button.style.marginLeft = '8px';
      button.addEventListener('click', () => {
        flags.pendingActivationBypass.add(el);
        try { el.click(); } finally { flags.pendingActivationBypass.delete(el); }
      });
      el.insertAdjacentElement('afterend', button);
      flags.pendingActivation.add(el);
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installGitlabSortDropdownPendingApply = () => {
    const items = targetNodes();
    const button = items[0];
    if (!button) return {installed: false, reason: 'sort dropdown button not found'};
    if (flags.gitlabSortButton.has(button)) return {installed: true, reused: true};
    const wrap = button.closest('.js-project-filter-dropdown-wrap') || button.parentElement;
    const state = {pendingHref: null, pendingText: null};
    const menuSelector = SPEC.menu_selector || '#project-filter-form .js-project-filter-dropdown-wrap .dropdown-menu a[href*=sort=]';
    const dropdownItems = () => nodes(menuSelector).filter((el) => wrap ? wrap.contains(el) : true);
    const apply = document.createElement('button');
    apply.type = 'button';
    apply.textContent = SPEC.apply_label || 'Apply sort';
    apply.setAttribute('aria-disabled', 'true');
    apply.disabled = true;
    apply.style.marginLeft = '8px';
    apply.style.whiteSpace = 'nowrap';
    const updateApply = () => {
      if (state.pendingHref) {
        apply.disabled = false;
        apply.setAttribute('aria-disabled', 'false');
        apply.textContent = (SPEC.apply_label || 'Apply sort') + ': ' + (state.pendingText || 'selected option');
      } else {
        apply.disabled = true;
        apply.setAttribute('aria-disabled', 'true');
        apply.textContent = SPEC.apply_label || 'Apply sort';
      }
    };
    const closeMenu = () => {
      if (wrap) wrap.classList.remove('show');
      const menu = wrap && wrap.querySelector('.dropdown-menu');
      if (menu) menu.classList.remove('show');
      button.setAttribute('aria-expanded', 'false');
    };
    const setPending = (link) => {
      const href = link.getAttribute('href');
      if (!href) return;
      state.pendingHref = href;
      state.pendingText = (link.innerText || link.textContent || '').trim().replace(/\s+/g, ' ');
      button.textContent = state.pendingText || button.textContent;
      closeMenu();
      updateApply();
      button.focus({preventScroll: false});
      log('gitlab_sort_pending', {href: state.pendingHref, text: state.pendingText});
    };
    const repairItems = () => {
      const links = dropdownItems();
      links.forEach((link) => {
        makeFocusable(link);
        if (flags.gitlabSortItem.has(link)) return;
        link.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          setPending(link);
        }, true);
        link.addEventListener('keydown', (event) => {
          if (!isActivationKey(event)) return;
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          setPending(link);
        }, true);
        flags.gitlabSortItem.add(link);
      });
      return links;
    };
    button.addEventListener('keydown', (event) => {
      if (!(isActivationKey(event) || event.key === 'ArrowDown')) return;
      setTimeout(() => {
        const links = repairItems();
        if (links.length) links[0].focus({preventScroll: false});
      }, 0);
      setTimeout(repairItems, 80);
    }, true);
    button.addEventListener('click', () => { setTimeout(repairItems, 0); setTimeout(repairItems, 80); }, true);
    apply.addEventListener('click', () => {
      if (!state.pendingHref) return;
      const href = state.pendingHref;
      log('gitlab_sort_apply', {href, text: state.pendingText});
      if (/^https?:\/\//.test(href)) window.location.href = href;
      else window.location.href = new URL(href, window.location.href).href;
    });
    button.insertAdjacentElement('afterend', apply);
    repairItems();
    updateApply();
    flags.gitlabSortButton.add(button);
    return {installed: true, count: 1};
  };

  const installGitlabSidebarToggleRepair = () => {
    const items = targetNodes();
    items.forEach((el) => {
      makeFocusable(el);
      el.setAttribute('role', 'button');
      el.setAttribute('aria-label', SPEC.aria_label || 'Toggle sidebar');
      const labelText = () => {
        const sidebar = document.querySelector('aside');
        return sidebar && sidebar.classList.contains('sidebar-collapsed-desktop') ? '>> Expand sidebar' : '<< Collapse sidebar';
      };
      let label = refs.sidebarLabelByToggle.get(el);
      if (!label) {
        label = document.createElement('span');
        refs.sidebarLabelByToggle.set(el, label);
        el.appendChild(label);
      }
      const originalText = el.querySelector('.collapse-text');
      if (originalText && originalText !== label) originalText.style.setProperty('display', 'none', 'important');
      const originalIcon = el.querySelector('svg');
      if (originalIcon) originalIcon.style.setProperty('display', 'none', 'important');
      const renderLabel = () => {
        label.textContent = labelText();
        label.style.setProperty('display', 'inline-flex', 'important');
        label.style.setProperty('align-items', 'center', 'important');
        label.style.setProperty('justify-content', 'center', 'important');
        label.style.setProperty('width', '100%', 'important');
        label.style.setProperty('gap', '8px', 'important');
        label.style.setProperty('padding', '8px 12px', 'important');
        label.style.setProperty('border', '2px solid #ffffff', 'important');
        label.style.setProperty('border-radius', '4px', 'important');
        label.style.setProperty('background', '#111827', 'important');
        label.style.setProperty('color', '#ffffff', 'important');
        label.style.setProperty('font', '800 15px Arial, sans-serif', 'important');
        label.style.setProperty('line-height', '20px', 'important');
        label.style.setProperty('white-space', 'nowrap', 'important');
      };
      renderLabel();
      el.style.setProperty('position', 'fixed', 'important');
      el.style.setProperty('left', '24px', 'important');
      el.style.setProperty('bottom', '24px', 'important');
      el.style.setProperty('z-index', '2147483000', 'important');
      el.style.setProperty('min-width', '260px', 'important');
      el.style.setProperty('width', '260px', 'important');
      el.style.setProperty('min-height', '64px', 'important');
      el.style.setProperty('height', '64px', 'important');
      el.style.setProperty('padding', '6px', 'important');
      el.style.setProperty('margin', '0', 'important');
      el.style.setProperty('border', '3px solid #111827', 'important');
      el.style.setProperty('border-radius', '6px', 'important');
      el.style.setProperty('background-color', '#facc15', 'important');
      el.style.setProperty('color', '#111827', 'important');
      el.style.setProperty('display', 'flex', 'important');
      el.style.setProperty('align-items', 'center', 'important');
      el.style.setProperty('justify-content', 'center', 'important');
      el.style.setProperty('gap', '8px', 'important');
      el.style.setProperty('box-sizing', 'border-box', 'important');
      el.style.setProperty('outline-offset', '-4px', 'important');
      el.style.setProperty('scroll-margin-top', '72px', 'important');
      el.style.setProperty('scroll-margin-bottom', '96px', 'important');
      if (!flags.sidebarToggle.has(el)) {
        const showFocus = () => {
          renderLabel();
          try { el.scrollIntoView({block: 'center', inline: 'nearest'}); } catch (_) {}
          el.style.setProperty('outline', '3px solid #1f75cb', 'important');
          el.style.setProperty('box-shadow', '0 0 0 3px #ffffff, 0 0 0 6px #1f75cb', 'important');
          el.style.setProperty('background-color', '#fff7ed', 'important');
          el.style.setProperty('color', '#111827', 'important');
        };
        const clearFocus = () => {
          el.style.removeProperty('outline');
          el.style.removeProperty('box-shadow');
          el.style.removeProperty('background-color');
          el.style.removeProperty('color');
        };
        el.addEventListener('focusin', () => { setTimeout(showFocus, 0); }, true);
        el.addEventListener('blur', clearFocus, true);
        el.addEventListener('keydown', (event) => {
          if (!isActivationKey(event)) return;
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          el.click();
          setTimeout(() => { renderLabel(); showFocus(); }, 0);
          log('sidebar_toggle_keyboard_activate', {text: (el.innerText || el.textContent || '').trim().slice(0, 80)});
        }, true);
        flags.sidebarToggle.add(el);
      }
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installGitlabChartLegendRepair = () => {
    const items = targetNodes();
    items.forEach((el, index) => {
      makeFocusable(el);
      el.setAttribute('role', 'button');
      const text = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ') || ('Chart series ' + (index + 1));
      el.setAttribute('aria-label', SPEC.aria_label_prefix ? SPEC.aria_label_prefix + ' ' + text : 'Toggle chart series ' + text);
      el.style.setProperty('display', 'inline-flex', 'important');
      el.style.setProperty('align-items', 'center', 'important');
      el.style.setProperty('justify-content', 'center', 'important');
      el.style.setProperty('min-width', '96px', 'important');
      el.style.setProperty('min-height', '36px', 'important');
      el.style.setProperty('margin', '4px 8px 4px 0', 'important');
      el.style.setProperty('padding', '7px 12px', 'important');
      el.style.setProperty('border', '2px solid #1f2937', 'important');
      el.style.setProperty('border-radius', '6px', 'important');
      el.style.setProperty('background-color', '#ffffff', 'important');
      el.style.setProperty('color', '#111827', 'important');
      el.style.setProperty('font', '700 14px Arial, sans-serif', 'important');
      el.style.setProperty('line-height', '18px', 'important');
      el.style.setProperty('box-sizing', 'border-box', 'important');
      el.style.setProperty('cursor', 'pointer', 'important');
      el.style.setProperty('scroll-margin-top', '96px', 'important');
      const label = el.querySelector('.gl-series-label-text');
      if (label) label.style.setProperty('font-weight', '800', 'important');
      if (!flags.chartLegend.has(el)) {
        const showFocus = () => {
          try { el.scrollIntoView({block: 'center', inline: 'nearest'}); } catch (_) {}
          el.style.setProperty('outline', '3px solid #1f75cb', 'important');
          el.style.setProperty('box-shadow', '0 0 0 3px #ffffff, 0 0 0 6px #1f75cb', 'important');
          el.style.setProperty('background-color', '#eff6ff', 'important');
        };
        const clearFocus = () => {
          el.style.removeProperty('outline');
          el.style.removeProperty('box-shadow');
          el.style.setProperty('background-color', '#ffffff', 'important');
        };
        el.addEventListener('focusin', () => { setTimeout(showFocus, 0); }, true);
        el.addEventListener('blur', clearFocus, true);
        el.addEventListener('keydown', (event) => {
          if (!isActivationKey(event)) return;
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          el.click();
          setTimeout(showFocus, 0);
          log('chart_legend_keyboard_activate', {text});
        }, true);
        flags.chartLegend.add(el);
      }
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installRedditSortDropdownPendingApply = () => {
    const items = targetNodes();
    const button = items[0];
    if (!button) return {installed: false, reason: 'reddit sort button not found'};
    if (flags.redditSortButton.has(button)) return {installed: true, reused: true};
    const wrap = button.closest('.dropdown') || button.parentElement;
    const state = {pendingHref: null, pendingText: null};
    const menuItems = () => Array.from((wrap || document).querySelectorAll('.menu-item[href], a[href]')).filter((el) => visible(el));
    const apply = document.createElement('button');
    apply.type = 'button';
    apply.textContent = SPEC.apply_label || 'Apply sort';
    apply.setAttribute('aria-disabled', 'true');
    apply.disabled = true;
    apply.style.setProperty('margin-left', '8px', 'important');
    apply.style.setProperty('min-height', '34px', 'important');
    apply.style.setProperty('padding', '5px 10px', 'important');
    apply.style.setProperty('border', '2px solid #1f2937', 'important');
    apply.style.setProperty('border-radius', '4px', 'important');
    apply.style.setProperty('background', '#ffffff', 'important');
    apply.style.setProperty('color', '#111827', 'important');
    apply.style.setProperty('font', '700 14px Arial, sans-serif', 'important');
    const updateApply = () => {
      if (state.pendingHref) {
        apply.disabled = false;
        apply.setAttribute('aria-disabled', 'false');
        apply.textContent = (SPEC.apply_label || 'Apply sort') + ': ' + (state.pendingText || 'selected option');
      } else {
        apply.disabled = true;
        apply.setAttribute('aria-disabled', 'true');
        apply.textContent = SPEC.apply_label || 'Apply sort';
      }
    };
    const closeMenu = () => {
      if (wrap) wrap.classList.remove('dropdown--expanded');
      button.setAttribute('aria-expanded', 'false');
    };
    const setPending = (link) => {
      const href = link.getAttribute('href');
      if (!href) return;
      state.pendingHref = href;
      state.pendingText = (link.innerText || link.textContent || '').trim().replace(/\s+/g, ' ');
      const textNode = button.querySelector('.no-underline__exempt');
      if (textNode && state.pendingText) textNode.textContent = state.pendingText;
      closeMenu();
      updateApply();
      button.focus({preventScroll: false});
      log('reddit_sort_pending', {href: state.pendingHref, text: state.pendingText});
    };
    const repairItems = () => {
      const links = menuItems();
      links.forEach((link) => {
        makeFocusable(link);
        if (flags.redditSortItem.has(link)) return;
        link.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          setPending(link);
        }, true);
        link.addEventListener('keydown', (event) => {
          if (!isActivationKey(event)) return;
          event.preventDefault();
          event.stopImmediatePropagation();
          event.stopPropagation();
          setPending(link);
        }, true);
        flags.redditSortItem.add(link);
      });
      return links;
    };
    button.addEventListener('keydown', (event) => {
      if (!(isActivationKey(event) || event.key === 'ArrowDown')) return;
      setTimeout(() => {
        const links = repairItems();
        if (links.length) links[0].focus({preventScroll: false});
      }, 0);
      setTimeout(repairItems, 80);
    }, true);
    button.addEventListener('click', () => { setTimeout(repairItems, 0); setTimeout(repairItems, 80); }, true);
    apply.addEventListener('click', () => {
      if (!state.pendingHref) return;
      const href = state.pendingHref;
      log('reddit_sort_apply', {href, text: state.pendingText});
      if (/^https?:\/\//.test(href)) window.location.href = href;
      else window.location.href = new URL(href, window.location.href).href;
    });
    button.insertAdjacentElement('afterend', apply);
    repairItems();
    updateApply();
    flags.redditSortButton.add(button);
    return {installed: true, count: 1};
  };

  const installShortcutScopeLimit = () => {
    if (shortcutScopeInstalled) return {installed: true, reused: true};
    const keys = (SPEC.blocked_keys || ['/', '?']).map(String);
    const isEditable = (el) => {
      if (!el) return false;
      const tag = el.tagName ? el.tagName.toLowerCase() : '';
      return el.isContentEditable || ['input', 'textarea', 'select'].includes(tag);
    };
    window.addEventListener('keydown', (event) => {
      if (keys.includes(event.key) && !isEditable(document.activeElement)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        log('shortcut_blocked', {key: event.key});
      }
    }, true);
    shortcutScopeInstalled = true;
    return {installed: true, blocked_keys: keys};
  };

  const installEditorTabEscape = () => {
    const targets = targetNodes();
    const focusables = () => nodes('a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])').filter((el) => visible(el) && !el.disabled && el.getAttribute('aria-disabled') !== 'true');
    const movePastEditor = (from, reverse) => {
      const editor = from.closest('.monaco-editor') || from;
      const list = focusables();
      const idx = list.findIndex((el) => el === from || from.contains(el) || editor.contains(el));
      const next = reverse ? list.slice(0, Math.max(0, idx)).reverse().find((el) => !editor.contains(el)) : list.slice(Math.max(0, idx + 1)).find((el) => !editor.contains(el));
      if (!next) return false;
      next.focus({preventScroll: false});
      log('editor_tab_escape', {reverse, tag: next.tagName, id: next.id || null});
      return true;
    };
    targets.forEach((el) => {
      if (flags.editorEscape.has(el)) return;
      el.addEventListener('keydown', (event) => {
        if (event.key !== 'Tab') return;
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        movePastEditor(el, event.shiftKey);
      }, true);
      flags.editorEscape.add(el);
    });
    return {installed: targets.length > 0, count: targets.length};
  };

  const installJqueryUiDatepickerNavRepair = () => {
    if (jqueryDatepickerState) {
      if (typeof jqueryDatepickerRefresh === 'function') {
        return Object.assign({installed: true, reused: true}, jqueryDatepickerRefresh());
      }
      return {installed: true, reused: true};
    }
    const state = {activeControl: null, activePanelItemKind: null, activeNavKind: null, keyboardUntil: 0, allowHideUntil: 0};
    const panel = () => document.querySelector('#ui-datepicker-div');
    const panelVisible = () => {
      const p = panel();
      return !!(p && visible(p));
    };
    const dateControlSelector = 'button.ui-datepicker-trigger, input.hasDatepicker, input._has-datepicker, input[id*=date], input[name*=date]';
    const dateControlFor = (target) => {
      if (!target || !target.closest) return null;
      const control = target.closest(dateControlSelector);
      return control && visible(control) ? control : null;
    };
    const dateControls = () => nodes(dateControlSelector).filter(visible);
    const navKind = (el) => el && el.classList && el.classList.contains('ui-datepicker-next') ? 'next' : 'prev';
    const navs = () => {
      const p = panel();
      if (!p || !visible(p)) return [];
      return nodes(selector).filter((el) => p.contains(el) && visible(el));
    };
    const itemKind = (el) => {
      if (!el) return 'unknown';
      if (el.classList && el.classList.contains('ui-datepicker-prev')) return 'prev';
      if (el.classList && el.classList.contains('ui-datepicker-next')) return 'next';
      if (el.classList && el.classList.contains('ui-datepicker-month')) return 'month';
      if (el.classList && el.classList.contains('ui-datepicker-year')) return 'year';
      if (el.classList && el.classList.contains('ui-datepicker-current')) return 'today';
      if (el.classList && el.classList.contains('ui-datepicker-close')) return 'close';
      if (el.classList && el.classList.contains('ui-state-default')) return 'day';
      return (el.tagName || 'item').toLowerCase();
    };
    const panelItems = () => {
      const p = panel();
      if (!p || !visible(p)) return [];
      const preferred = [
        '.ui-datepicker-prev',
        '.ui-datepicker-next',
        'select.ui-datepicker-month',
        'select.ui-datepicker-year',
        'td:not(.ui-datepicker-unselectable) a.ui-state-default',
        'button.ui-datepicker-current',
        'button.ui-datepicker-close',
        'a[href]',
        'button',
        'select',
        'input',
        '[role="button"]',
        '[tabindex]',
      ];
      const out = [];
      for (const sel of preferred) {
        for (const el of Array.from(p.querySelectorAll(sel))) {
          if (out.includes(el) || !visible(el) || el.disabled || el.getAttribute('aria-disabled') === 'true') continue;
          out.push(el);
        }
      }
      return out;
    };
    const showForKeyboard = () => {
      const p = panel();
      if (!p) return;
      p.style.display = 'block';
      p.style.visibility = 'visible';
      p.removeAttribute('aria-hidden');
    };
    const hidePanel = () => {
      const p = panel();
      try {
        const jq = window.jQuery || window.$;
        state.allowHideUntil = Date.now() + 500;
        if (jq && jq.datepicker && typeof jq.datepicker._hideDatepicker === 'function') jq.datepicker._hideDatepicker();
        if (jq && jq.datepicker) {
          jq.datepicker._datepickerShowing = false;
          jq.datepicker._lastInput = null;
        }
      } catch (_) {}
      if (!p) return;
      p.style.display = 'none';
      p.setAttribute('aria-hidden', 'true');
    };
    const readyItem = (el) => {
      if (!el) return;
      const kind = itemKind(el);
      makeFocusable(el);
      el.style.setProperty('scroll-margin-top', '96px', 'important');
      if ((kind === 'prev' || kind === 'next' || kind === 'day') && !el.getAttribute('role') && el.tagName.toLowerCase() !== 'button') el.setAttribute('role', 'button');
      if (!el.getAttribute('aria-label')) {
        if (kind === 'next') el.setAttribute('aria-label', 'Next month');
        else if (kind === 'prev') el.setAttribute('aria-label', 'Previous month');
        else if (kind === 'month') el.setAttribute('aria-label', 'Select month');
        else if (kind === 'year') el.setAttribute('aria-label', 'Select year');
        else if (kind === 'day') el.setAttribute('aria-label', 'Select day ' + ((el.innerText || el.textContent || '').trim() || 'date'));
      }
    };
    const readyNav = (el) => {
      readyItem(el);
    };
    const repair = () => {
      const items = panelItems();
      items.forEach((el) => {
        readyItem(el);
        if (flags.jqueryDatepickerItem.has(el)) return;
        el.addEventListener('focusin', () => {
          const kind = itemKind(el);
          state.activePanelItemKind = kind;
          state.activeNavKind = kind === 'next' || kind === 'prev' ? kind : null;
          state.keyboardUntil = Date.now() + 1500;
          showForKeyboard();
          el.style.setProperty('outline', '4px solid #1f75cb', 'important');
          el.style.setProperty('outline-offset', '2px', 'important');
          el.style.setProperty('box-shadow', '0 0 0 4px #ffffff, 0 0 0 8px #1f75cb', 'important');
        }, true);
        el.addEventListener('blur', () => {
          el.style.removeProperty('outline');
          el.style.removeProperty('outline-offset');
          el.style.removeProperty('box-shadow');
        }, true);
        el.addEventListener('change', () => {
          state.activePanelItemKind = itemKind(el);
          state.keyboardUntil = Date.now() + 1500;
          setTimeout(() => { showForKeyboard(); repair(); focusPanelKind(state.activePanelItemKind); }, 0);
          setTimeout(() => { showForKeyboard(); repair(); focusPanelKind(state.activePanelItemKind); }, 80);
        }, true);
        el.addEventListener('keydown', (event) => {
          const current = itemKind(el);
          if (event.key === 'Tab') {
            const all = panelItems();
            const i = all.indexOf(el);
            const next = event.shiftKey ? all[i - 1] : all[i + 1];
            if (next) {
              event.preventDefault();
              event.stopImmediatePropagation();
              event.stopPropagation();
              const nextKind = itemKind(next);
              state.activePanelItemKind = nextKind;
              state.activeNavKind = nextKind === 'next' || nextKind === 'prev' ? nextKind : null;
              state.keyboardUntil = Date.now() + 1500;
              showForKeyboard();
              readyItem(next);
              next.focus({preventScroll: false});
            } else {
              state.activePanelItemKind = null;
              state.activeNavKind = null;
              state.keyboardUntil = 0;
              if (!event.shiftKey) hidePanel();
            }
          } else if (isActivationKey(event)) {
            if (el.tagName && ['select', 'input', 'textarea'].includes(el.tagName.toLowerCase())) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            event.stopPropagation();
            state.activePanelItemKind = current;
            state.activeNavKind = current === 'next' || current === 'prev' ? current : null;
            state.keyboardUntil = Date.now() + 1500;
            showForKeyboard();
            dispatchMouseActivation(el);
            if (current === 'close') {
              setTimeout(hidePanel, 0);
            } else if (current === 'day' || current === 'today') {
              state.keyboardUntil = 0;
            } else {
              setTimeout(() => { repair(); focusPanelKind(current); }, 0);
              setTimeout(() => { repair(); focusPanelKind(current); }, 80);
            }
          }
        }, true);
        flags.jqueryDatepickerItem.add(el);
      });
      return items;
    };
    function focusPanelKind(kind) {
      if (!panelVisible() && Date.now() > state.keyboardUntil) return false;
      showForKeyboard();
      const item = repair().find((el) => itemKind(el) === kind) || repair()[0];
      if (!item) return false;
      state.activePanelItemKind = itemKind(item);
      state.activeNavKind = state.activePanelItemKind === 'next' || state.activePanelItemKind === 'prev' ? state.activePanelItemKind : null;
      state.keyboardUntil = Date.now() + 1500;
      item.focus({preventScroll: false});
      return document.activeElement === item;
    }
    function focusNav(kind) { return focusPanelKind(kind); }
    const rememberControl = (control) => {
      if (!control) return;
      state.activeControl = control;
      setTimeout(repair, 0);
      setTimeout(repair, 80);
    };
    const patchHide = () => {
      const jq = window.jQuery || window.$;
      if (!jq || !jq.datepicker || jqueryDatepickerHidePatched || typeof jq.datepicker._hideDatepicker !== 'function') return;
      const originalHide = jq.datepicker._hideDatepicker;
      jq.datepicker._hideDatepicker = function() {
        if (Date.now() < state.allowHideUntil) return originalHide.apply(this, arguments);
        if (Date.now() < state.keyboardUntil && state.activeControl) {
          showForKeyboard();
          setTimeout(() => { showForKeyboard(); repair(); }, 0);
          return;
        }
        return originalHide.apply(this, arguments);
      };
      jqueryDatepickerHidePatched = true;
    };
    patchHide();
    document.addEventListener('pointerdown', (event) => {
      const control = dateControlFor(event.target);
      if (control) {
        rememberControl(control);
        return;
      }
      const p = panel();
      if (!p || !event.target || !p.contains(event.target)) {
        state.activeNavKind = null;
        state.keyboardUntil = 0;
      }
    }, true);
    document.addEventListener('click', (event) => {
      const control = dateControlFor(event.target);
      if (control) rememberControl(control);
    }, true);
    document.addEventListener('focusin', (event) => {
      const control = dateControlFor(event.target);
      if (control) rememberControl(control);
      const p = panel();
      if (p && event.target && p.contains(event.target)) {
        state.activePanelItemKind = itemKind(event.target);
        state.keyboardUntil = Date.now() + 1500;
        showForKeyboard();
      }
    }, true);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        state.activePanelItemKind = null;
        state.activeNavKind = null;
        state.keyboardUntil = 0;
        if (panelVisible()) hidePanel();
        return;
      }
      if (event.key !== 'Tab' || event.shiftKey) return;
      const active = document.activeElement;
      if (!active || !dateControlFor(active) || !panelVisible()) return;
      const items = repair();
      if (!items.length) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      event.stopPropagation();
      state.activePanelItemKind = itemKind(items[0]);
      state.activeNavKind = state.activePanelItemKind === 'next' || state.activePanelItemKind === 'prev' ? state.activePanelItemKind : null;
      state.keyboardUntil = Date.now() + 1500;
      showForKeyboard();
      items[0].focus({preventScroll: false});
    }, true);
    if (panelVisible()) repair();
    jqueryDatepickerState = state;
    jqueryDatepickerRefresh = () => {
      patchHide();
      const items = repair();
      return {dateControlCount: dateControls().length, panelVisible: panelVisible(), count: items.length, navCount: navs().length};
    };
    return {installed: dateControls().length > 0 || !!panel(), dateControlCount: dateControls().length, panelVisible: panelVisible(), count: panelItems().length, navCount: navs().length};
  };

  const installGitlabModalDropdownRepair = () => {
    const items = targetNodes();
    items.forEach((el) => {
      makeFocusable(el);
      if (flags.gitlabModalDropdown.has(el)) return;
      el.addEventListener('keydown', (event) => {
        if (!(isActivationKey(event) || event.key === 'ArrowDown')) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        dispatchMouseActivation(el);
        const focusSearch = () => {
          const input = document.querySelector('.modal-dialog .dropdown-menu.show .gl-listbox-search-input, .modal-dialog .dropdown-menu .gl-listbox-search-input, .modal-dialog input[type="search"], .modal-dialog input[role="combobox"]');
          if (input && visible(input)) input.focus({preventScroll: false});
        };
        setTimeout(focusSearch, 0);
        setTimeout(focusSearch, 80);
        log('modal_dropdown_key_open', {key: event.key});
      }, true);
      flags.gitlabModalDropdown.add(el);
    });
    return {installed: items.length > 0, count: items.length};
  };

  const installGitlabPikaSingleRepair = () => {
    const inputSelector = SPEC.input_selector || '#personal_access_token_expires_at';
    const input = document.querySelector(inputSelector);
    if (!input) return {installed: false, reason: 'input not found', input_selector: inputSelector};
    if (gitlabPikaSingleState) return {installed: true, reused: true};
    const state = {lastNavKind: null, keyboardUntil: 0, openUntil: 0};
    const getDp = () => { try { return input.__vue__ && input.__vue__.$parent && input.__vue__.$parent.$parent; } catch (_) { return null; } };
    const getCalendar = () => { const dp = getDp(); return dp && dp.calendar; };
    const getPanel = () => { const calendar = getCalendar(); return calendar && (calendar.el || (calendar._o && calendar._o.container)) || document.querySelector('.pika-single'); };
    const showPanel = () => { const p = getPanel(); if (!p) return null; p.classList.remove('is-hidden'); p.style.display = ''; p.removeAttribute('aria-hidden'); return p; };
    const openPicker = (reason) => {
      const dp = getDp(); const calendar = getCalendar();
      if (!dp || !calendar) return null;
      if (String(reason).startsWith('pointer') || String(reason).startsWith('click') || String(reason).startsWith('focus')) state.openUntil = Date.now() + 1200;
      try { if (typeof dp.show === 'function') dp.show(); } catch (_) {}
      try { if (typeof calendar.show === 'function') calendar.show(); } catch (_) {}
      try { if (typeof calendar.adjustPosition === 'function') calendar.adjustPosition(); } catch (_) {}
      showPanel(); repairNavs(); return {dp, calendar};
    };
    const navFor = (kind) => { const p = showPanel(); return p && p.querySelector(kind === 'next' ? '.pika-next' : '.pika-prev'); };
    const readyNav = (nav, kind) => { if (!nav) return; makeFocusable(nav); if (!nav.getAttribute('aria-label')) nav.setAttribute('aria-label', kind === 'next' ? 'Next month' : 'Previous month'); };
    const focusNav = (kind) => { openPicker('focus-nav'); const nav = navFor(kind); if (!nav) return false; readyNav(nav, kind); state.lastNavKind = kind; state.keyboardUntil = Date.now() + 700; nav.focus({preventScroll: false}); return document.activeElement === nav; };
    const refocus = (kind) => { setTimeout(() => focusNav(kind), 0); setTimeout(() => focusNav(kind), 40); };
    const protectNav = () => state.lastNavKind && Date.now() < state.keyboardUntil;
    const protectOpen = () => Date.now() < state.openUntil;
    const activateNav = (kind) => { const calendar = getCalendar(); if (!calendar) return false; state.keyboardUntil = Date.now() + 700; try { if (kind === 'prev' && typeof calendar.prevMonth === 'function') calendar.prevMonth(); if (kind === 'next' && typeof calendar.nextMonth === 'function') calendar.nextMonth(); } catch (_) {} try { if (typeof calendar.draw === 'function') calendar.draw(true); } catch (_) {} showPanel(); repairNavs(); refocus(kind); log('pika_nav_activate', {kind}); return true; };
    function repairNavs() {
      for (const kind of ['prev', 'next']) {
        const nav = navFor(kind); readyNav(nav, kind); if (!nav || flags.gl15Nav.has(nav)) continue;
        nav.addEventListener('keydown', (event) => {
          const current = nav.classList.contains('pika-next') ? 'next' : 'prev';
          if (event.key === 'Tab') {
            const next = event.shiftKey ? (current === 'next' ? 'prev' : null) : (current === 'prev' ? 'next' : null);
            if (next) { event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); focusNav(next); }
            else { state.lastNavKind = null; state.keyboardUntil = 0; }
          } else if (isActivationKey(event)) { event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); activateNav(current); }
        }, true);
        nav.addEventListener('focusin', () => { state.lastNavKind = nav.classList.contains('pika-next') ? 'next' : 'prev'; state.keyboardUntil = Date.now() + 700; showPanel(); }, true);
        flags.gl15Nav.add(nav);
      }
    }
    const calendar = getCalendar();
    if (calendar && !flags.gl15Calendar.has(calendar)) {
      const originalHide = calendar.hide;
      calendar.hide = function() { if (protectNav() || protectOpen()) { showPanel(); return; } return originalHide ? originalHide.apply(this, arguments) : undefined; };
      const originalBlur = calendar._onInputBlur;
      calendar._onInputBlur = function() { if (protectNav() || protectOpen()) { showPanel(); return; } return originalBlur ? originalBlur.apply(this, arguments) : undefined; };
      flags.gl15Calendar.add(calendar);
    }
    input.addEventListener('pointerdown', () => { state.lastNavKind = null; state.keyboardUntil = 0; state.openUntil = Date.now() + 1200; openPicker('pointerdown'); setTimeout(() => openPicker('pointerdown:80'), 80); }, true);
    input.addEventListener('click', () => { state.openUntil = Date.now() + 1200; openPicker('click'); setTimeout(() => openPicker('click:50'), 50); setTimeout(() => openPicker('click:150'), 150); }, false);
    input.addEventListener('focusin', () => { if (protectNav()) { refocus(state.lastNavKind); return; } openPicker('focusin'); }, true);
    input.addEventListener('keydown', (event) => { if (event.key !== 'Tab' || event.shiftKey) return; event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); openPicker('tab-from-input'); focusNav('prev'); }, true);
    gitlabPikaSingleState = state;
    return {installed: true, input_selector: inputSelector};
  };

  const installGitlabPikaRangeRepair = () => {
    if (gitlabPikaRangeState) return {installed: true, reused: true};
    const state = {activeRoot: null, activePanel: null, lastNavKind: null, keyboardUntil: 0, openUntil: 0};
    const roots = () => Array.from(document.querySelectorAll(SPEC.root_selector || '.gl-datepicker'));
    const infoForRoot = (root) => {
      const input = root ? root.querySelector('input') : null;
      let dp = null;
      try { dp = input && input.__vue__ && input.__vue__.$parent && input.__vue__.$parent.$parent; } catch (_) {}
      const calendar = dp && dp.calendar;
      const panel = calendar && (calendar.el || (calendar._o && calendar._o.container));
      return {root, input, dp, calendar, panel};
    };
    const allInfos = () => roots().map(infoForRoot);
    const showPanel = (panel) => { if (!panel) return; panel.classList.remove('is-hidden'); panel.style.display = ''; panel.removeAttribute('aria-hidden'); };
    const hidePanel = (panel) => { if (!panel) return; panel.classList.add('is-hidden'); panel.style.display = 'none'; panel.setAttribute('aria-hidden', 'true'); };
    const setActiveRoot = (root, reason) => {
      const info = infoForRoot(root);
      if (!info.root || !info.dp || !info.calendar || !info.panel) return null;
      state.activeRoot = info.root; state.activePanel = info.panel;
      if (String(reason).startsWith('pointer') || String(reason).startsWith('click')) state.openUntil = Date.now() + 1200;
      for (const other of allInfos()) if (other.root !== info.root) hidePanel(other.panel);
      try { if (typeof info.dp.show === 'function') info.dp.show(); } catch (_) {}
      try { if (typeof info.calendar.show === 'function') info.calendar.show(); } catch (_) {}
      try { if (typeof info.calendar.adjustPosition === 'function') info.calendar.adjustPosition(); } catch (_) {}
      showPanel(info.panel); repairNavs(info); return info;
    };
    const currentInfo = () => {
      if (state.activeRoot && document.contains(state.activeRoot)) {
        const info = infoForRoot(state.activeRoot);
        if (info.dp && info.calendar && info.panel) return info;
      }
      return null;
    };
    const navFor = (info, kind) => info && info.panel ? info.panel.querySelector(kind === 'next' ? '.pika-next' : '.pika-prev') : null;
    const readyNav = (nav, kind) => { if (!nav) return; makeFocusable(nav); if (!nav.getAttribute('aria-label')) nav.setAttribute('aria-label', kind === 'next' ? 'Next month' : 'Previous month'); };
    const focusNav = (kind) => { const info = currentInfo(); if (!info) return false; showPanel(info.panel); repairNavs(info); const nav = navFor(info, kind); if (!nav) return false; readyNav(nav, kind); state.lastNavKind = kind; state.keyboardUntil = Date.now() + 700; nav.focus({preventScroll: false}); return document.activeElement === nav; };
    const refocus = (kind) => { setTimeout(() => focusNav(kind), 0); setTimeout(() => focusNav(kind), 40); };
    const protectNav = () => state.lastNavKind && Date.now() < state.keyboardUntil;
    const protectOpen = (root) => state.activeRoot === root && Date.now() < state.openUntil;
    const activateNav = (kind) => { const info = currentInfo(); if (!info || !info.calendar) return false; state.keyboardUntil = Date.now() + 700; try { if (kind === 'prev' && typeof info.calendar.prevMonth === 'function') info.calendar.prevMonth(); if (kind === 'next' && typeof info.calendar.nextMonth === 'function') info.calendar.nextMonth(); } catch (_) {} try { if (typeof info.calendar.draw === 'function') info.calendar.draw(true); } catch (_) {} showPanel(info.panel); repairNavs(info); refocus(kind); log('pika_range_nav_activate', {kind}); return true; };
    function repairNavs(info) {
      if (!info || !info.panel) return;
      for (const kind of ['prev', 'next']) {
        const nav = navFor(info, kind); readyNav(nav, kind); if (!nav || flags.gl82Nav.has(nav)) continue;
        nav.addEventListener('keydown', (event) => {
          const current = nav.classList.contains('pika-next') ? 'next' : 'prev';
          if (event.key === 'Tab') {
            const next = event.shiftKey ? (current === 'next' ? 'prev' : null) : (current === 'prev' ? 'next' : null);
            if (next) { event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); focusNav(next); }
            else { state.lastNavKind = null; state.keyboardUntil = 0; }
          } else if (isActivationKey(event)) { event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); activateNav(current); }
        }, true);
        nav.addEventListener('focusin', () => { state.lastNavKind = nav.classList.contains('pika-next') ? 'next' : 'prev'; state.keyboardUntil = Date.now() + 700; showPanel(info.panel); }, true);
        flags.gl82Nav.add(nav);
      }
    }
    for (const info of allInfos()) {
      if (!info.calendar || flags.gl82Calendar.has(info.calendar)) continue;
      const originalHide = info.calendar.hide;
      info.calendar.hide = function() { if (state.activeRoot === info.root && (protectNav() || protectOpen(info.root))) { showPanel(info.panel); return; } return originalHide ? originalHide.apply(this, arguments) : undefined; };
      const originalBlur = info.calendar._onInputBlur;
      info.calendar._onInputBlur = function(event) { if (state.activeRoot === info.root && (protectNav() || protectOpen(info.root))) { showPanel(info.panel); return; } return originalBlur ? originalBlur.apply(this, arguments) : undefined; };
      flags.gl82Calendar.add(info.calendar);
    }
    roots().forEach((root) => {
      if (flags.gl82Root.has(root)) return;
      root.addEventListener('pointerdown', (event) => { if (event.target && event.target.closest && event.target.closest('.pika-single')) return; state.lastNavKind = null; state.keyboardUntil = 0; state.activeRoot = root; state.openUntil = Date.now() + 1200; setActiveRoot(root, 'pointerdown'); setTimeout(() => setActiveRoot(root, 'pointerdown:80'), 80); }, true);
      root.addEventListener('click', (event) => { if (event.target && event.target.closest && event.target.closest('.pika-single')) return; state.openUntil = Date.now() + 1200; setActiveRoot(root, 'click-capture'); setTimeout(() => setActiveRoot(root, 'click'), 0); setTimeout(() => setActiveRoot(root, 'click:50'), 50); setTimeout(() => setActiveRoot(root, 'click:150'), 150); setTimeout(() => setActiveRoot(root, 'click:300'), 300); }, false);
      root.addEventListener('keydown', (event) => { if (event.key !== 'Tab' || event.shiftKey) return; const active = document.activeElement; if (!active || !root.contains(active) || (active.closest && active.closest('.pika-single'))) return; event.preventDefault(); event.stopImmediatePropagation(); event.stopPropagation(); setActiveRoot(root, 'tab-from-trigger'); focusNav('prev'); }, true);
      root.addEventListener('focusin', (event) => { if (event.target && event.target.closest && event.target.closest('.pika-single')) return; if (state.activeRoot === root && protectNav()) { event.stopImmediatePropagation(); event.stopPropagation(); refocus(state.lastNavKind); } }, true);
      flags.gl82Root.add(root);
    });
    gitlabPikaRangeState = state;
    return {installed: roots().length > 0, rootCount: roots().length};
  };

  const installers = {
    make_focusable_clickable: () => installMakeFocusable(true),
    make_focusable_no_activate: () => installMakeFocusable(false),
    gitlab_filtered_search_token_keyboard_repair: installGitlabFilteredSearchTokenRepair,
    magento_grid_actions_menu_keyboard_repair: installMagentoGridActionsMenuRepair,
    native_select_pending_apply: installNativeSelectPendingApply,
    activation_pending_apply: installActivationPendingApply,
    gitlab_sort_dropdown_pending_apply: installGitlabSortDropdownPendingApply,
    gitlab_sidebar_toggle_keyboard_repair: installGitlabSidebarToggleRepair,
    gitlab_chart_legend_keyboard_repair: installGitlabChartLegendRepair,
    reddit_sort_dropdown_pending_apply: installRedditSortDropdownPendingApply,
    global_shortcut_scope_limit: installShortcutScopeLimit,
    editor_tab_escape: installEditorTabEscape,
    datepicker_nav_keyboard_repair: installJqueryUiDatepickerNavRepair,
    gitlab_modal_dropdown_keyboard_repair: installGitlabModalDropdownRepair,
    gitlab_pika_single_datepicker_keyboard_repair: installGitlabPikaSingleRepair,
    gitlab_pika_range_datepicker_keyboard_repair: installGitlabPikaRangeRepair,
  };

  const install = () => {
    const fn = installers[SPEC.kind];
    if (!fn) throw new Error('Unsupported runtime repair kind: ' + SPEC.kind);
    const result = fn();
    lastInstallResult = {id: ID, kind: SPEC.kind, result};
    log('installed', result);
    return result;
  };
  let installedOnce = false;
  let observer = null;
  let retryCount = 0;
  const tryInstall = () => {
    try { install(); }
    catch (error) {
      lastInstallError = {id: ID, kind: SPEC.kind, message: String(error && error.message || error)};
      throw error;
    }
    const ready = lastInstallResult;
    const result = ready && ready.result;
    if (result && result.installed) {
      installedOnce = true;
      if (observer && SPEC.keep_observer !== true) {
        observer.disconnect();
        observer = null;
      }
    }
  };
  const start = () => {
    tryInstall();
    if (document.documentElement && !observer && !installedOnce) {
      observer = new MutationObserver(() => setTimeout(tryInstall, 0));
      observer.observe(document.documentElement, {childList: true, subtree: true, attributes: true});
    }
    const retry = setInterval(() => {
      retryCount += 1;
      tryInstall();
      if (installedOnce || retryCount >= 120) clearInterval(retry);
    }, 100);
  };
  if (document.documentElement) start();
  else document.addEventListener('DOMContentLoaded', start, {once: true});
})();
'''


def make_pass_l1_patch_script(task: TaskConfig, patch_spec: dict[str, Any]) -> str:
    return (
        PASS_L1_PATCH_JS.replace('__ID__', json.dumps(task.instance_id))
        .replace('__SPEC__', json.dumps(patch_spec))
        .replace('__TARGET__', json.dumps(task.target_selector or ''))
    )


async def run_task(
    task_path: Path,
    model: str,
    temperature: float,
    max_steps: int,
    headless: bool,
    auth_state_override: str | None = None,
    run_id: str | None = None,
    experiment_id: str | None = None,
    worker_id: int | None = None,
    session_batch_id: int | None = None,
    site: str | None = None,
    task_variant: str | None = None,
    repeat_index: int | None = None,
    queue_index: int | None = None,
    runs_root_override: str | None = None,
    capture_structured_failures: bool = False,
    disable_schema_enhancement: bool = False,
    salvage_multi_json: bool = False,
    reasoning_effort: str | None = None,
    prompt_footer_mode: str = 'full',
    highlight_elements: bool = False,
    current_focus_marker: bool = False,
    evidence_pack_manifest: str | None = None,
) -> Path:
    task = load_task(task_path)
    evaluate_rule_path = resolve_evaluate_rule(task_path, task)
    auth_state_path = resolve_optional_path(auth_state_override) if auth_state_override else resolve_optional_path(task.auth_state_file)
    evidence_pack_path = resolve_optional_path(evidence_pack_manifest)
    evidence_pack = (
        load_evidence_pack_manifest(
            evidence_pack_path,
            expected_task_id=task.task_id,
            expected_instance_id=task.instance_id,
            expected_family=task.issue_family,
        )
        if evidence_pack_path is not None
        else None
    )
    runs_root = resolve_runs_root(runs_root_override)
    patch_spec = pass_l1_patch_for_task(task_path, task)

    if auth_state_override and auth_state_path is not None and not auth_state_path.exists():
        raise FileNotFoundError('Auth state file not found: ' + str(auth_state_path))

    run_dir_name = run_id or datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = runs_root / build_task_output_dir_name(task.task_id) / run_dir_name
    conversation_dir = build_conversation_dir(run_dir)
    safe_mkdir(run_dir)
    safe_mkdir(conversation_dir)

    auth_state_refreshed = False
    auth_refresh_site = infer_site_from_task(task, site_override=site)
    if task.auth_state_file and not auth_state_override:
        if not auth_refresh_site:
            raise ValueError('Cannot infer site for auth refresh: ' + task.task_id)
        refreshed_auth_path = run_dir / 'refreshed_auth.storage_state.json'
        auth_state_path = await refresh_task_auth_state(auth_refresh_site, refreshed_auth_path, headless=True)
        probe_ok, probe_reason = await probe_task_auth_state(auth_refresh_site, auth_state_path)
        if not probe_ok:
            raise RuntimeError(f'Refreshed auth state failed probe for {auth_refresh_site}: {probe_reason}')
        auth_state_refreshed = True
    elif auth_state_override and auth_state_path is not None:
        if not auth_refresh_site:
            raise ValueError('Cannot infer site for auth probe: ' + task.task_id)
        probe_ok, probe_reason = await probe_task_auth_state(auth_refresh_site, auth_state_path)
        if not probe_ok:
            raise RuntimeError(f'Auth state override failed probe for {auth_refresh_site}: {probe_reason}')
    elif auth_state_path is not None and not auth_state_path.exists():
        raise FileNotFoundError('Auth state file not found: ' + str(auth_state_path))

    safe_copy2(task_path, run_dir / 'task.snapshot.yaml')
    if evaluate_rule_path is not None:
        safe_copy2(evaluate_rule_path, run_dir / 'evaluate-rule.snapshot.yaml')
    if evidence_pack is not None:
        safe_copy2(evidence_pack.path, run_dir / 'evidence-pack.snapshot.json')

    prompt_text = build_task_prompt(task)
    if evidence_pack is not None:
        prompt_text = append_evidence_pack_prompt(prompt_text, evidence_pack)
    write_text(run_dir / 'task.prompt.txt', prompt_text)
    write_text(run_dir / 'review.template.md', build_review_template(task, evaluate_rule_path))
    write_text(run_dir / 'conversation.path.txt', str(conversation_dir))

    previous_structured_debug_dir = os.environ.get('BROWSER_USE_STRUCTURED_DEBUG_DIR')
    if capture_structured_failures:
        structured_debug_dir = run_dir / 'spf'
        safe_mkdir(structured_debug_dir)
        os.environ['BROWSER_USE_STRUCTURED_DEBUG_DIR'] = str(structured_debug_dir)

    AgentClass, BrowserSessionClass = get_browser_use_classes()
    original_schema_enhancer = None
    if disable_schema_enhancement:
        original_schema_enhancer = getattr(AgentClass, '_enhance_task_with_schema', None)
        AgentClass._enhance_task_with_schema = lambda self, task_text, schema: task_text

    llm = create_task_llm(
        model=model,
        temperature=temperature,
        salvage_multi_json=salvage_multi_json,
        reasoning_effort=reasoning_effort,
    )
    storage_state = load_storage_state(auth_state_path)
    browser_storage_state_path = create_runtime_storage_state_file(storage_state, run_dir)
    browser_session = None

    meta = {
        'task_id': task.task_id,
        'instance_id': task.instance_id,
        'task_file': str(task_path),
        'evaluate_rule_file': str(evaluate_rule_path) if evaluate_rule_path else None,
        'model': model,
        'prompt_template_id': PROMPT_TEMPLATE_ID,
        'reasoning_effort': reasoning_effort,
        'temperature': temperature,
        'max_steps': max_steps,
        'headless': headless,
        'start_url': task.start_url,
        'run_started_at': datetime.now(timezone.utc).isoformat(),
        'run_id': run_dir_name,
        'experiment_id': experiment_id,
        'worker_id': worker_id,
        'session_batch_id': session_batch_id,
        'site': site,
        'task_variant': task_variant,
        'repeat_index': repeat_index,
        'queue_index': queue_index,
        'auth_state_file': str(auth_state_path) if auth_state_path else None,
        'auth_state_refreshed': auth_state_refreshed,
        'auth_refresh_site': auth_refresh_site,
        'runs_root': str(runs_root),
        'conversation_dir': str(conversation_dir),
        'capture_structured_failures': capture_structured_failures,
        'disable_schema_enhancement': disable_schema_enhancement,
        'salvage_multi_json': salvage_multi_json,
        'prompt_footer_mode': prompt_footer_mode,
        'highlight_elements': highlight_elements,
        'current_focus_marker': current_focus_marker,
        'evidence_pack_manifest': str(evidence_pack.path) if evidence_pack else None,
        'evidence_pack_candidate_count': len(evidence_pack.candidates) if evidence_pack else 0,
        'observation_condition': observation_condition_name(current_focus_marker=current_focus_marker, evidence_pack_enabled=evidence_pack is not None),
        'runtime_patch_applied': bool(patch_spec),
        'runtime_patch_manifest': str(PASS_L1_PATCH_MANIFEST) if patch_spec else None,
    }
    write_json(run_dir / 'meta.json', meta)

    try:
        browser_session = BrowserSessionClass(
            headless=headless,
            storage_state=browser_storage_state_path,
            viewport={'width': 1280, 'height': 900},
            window_size={'width': 1280, 'height': 900},
            enable_default_extensions=False,
            highlight_elements=highlight_elements,
            dom_highlight_elements=False,
        )
        if hasattr(browser_session, 'start'):
            await browser_session.start()
        if current_focus_marker:
            install_current_focus_marker(browser_session)
        if evidence_pack is not None:
            install_evidence_assisted_observation(browser_session, evidence_pack, debug_jsonl_path=run_dir / 'evidence-marker-resolution.jsonl')
        if patch_spec:
            await browser_session._cdp_add_init_script(make_pass_l1_patch_script(task, patch_spec))

        agent = AgentClass(
            task=prompt_text,
            llm=llm,
            browser_session=browser_session,
            output_model_schema=output_model_schema_for_task(task),
            use_vision=True,
            max_failures=5,
            max_actions_per_step=5,
            use_thinking=True,
            use_judge=False,
            llm_timeout=600,
            step_timeout=600,
            loop_detection_enabled=False,
            save_conversation_path=str(conversation_dir),
            generate_gif=str(run_dir / 'recording.gif'),
            directly_open_url=False,
            initial_actions=[{'navigate': {'url': task.start_url, 'new_tab': False}}],
        )
        write_text(run_dir / 'task.prompt.txt.final', agent.task or '')
        history = await agent.run(max_steps=max_steps)
        save_history_json(history, run_dir / 'history.json')
        write_json(run_dir / 'usage.json', build_usage_payload(history))

        final_result = history.final_result() or ''
        write_text(run_dir / 'final-response.txt', final_result)
        try:
            parsed_final = json.loads(final_result)
        except json.JSONDecodeError:
            parsed_final = {'raw': final_result}
        write_json(run_dir / 'final-response.json', parsed_final)

        meta.update({'run_finished_at': datetime.now(timezone.utc).isoformat(), 'agent_done': history.is_done(), 'agent_success': history.is_successful(), 'history_steps': len(history.history)})
        write_json(run_dir / 'meta.json', meta)
        return run_dir
    finally:
        if capture_structured_failures:
            if previous_structured_debug_dir is None:
                os.environ.pop('BROWSER_USE_STRUCTURED_DEBUG_DIR', None)
            else:
                os.environ['BROWSER_USE_STRUCTURED_DEBUG_DIR'] = previous_structured_debug_dir
        if disable_schema_enhancement and original_schema_enhancer is not None:
            AgentClass._enhance_task_with_schema = original_schema_enhancer
        await cleanup_browser_session(browser_session)
        cleanup_runtime_storage_state_file(browser_storage_state_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run one Keyboard GT verification task with browser-use.')
    parser.add_argument('--task', required=True, help='Task file name under agent/gt_keyboard/tasks or a path.')
    parser.add_argument('--print-prompt', action='store_true', help='Print the compact agent-facing prompt and exit.')
    parser.add_argument('--model', default='gpt-5.2-20251211', help='LLM model name for browser-use execution.')
    parser.add_argument('--reasoning-effort', help='Optional reasoning effort for LLM routes that support it.')
    parser.add_argument('--temperature', type=float, default=0, help='LLM temperature for verification runs.')
    parser.add_argument('--max-steps', type=int, default=25, help='Maximum browser-use agent steps.')
    parser.add_argument('--headless', action='store_true', help='Run the browser headlessly.')
    parser.add_argument('--auth-state-file', help='Optional auth state file override.')
    parser.add_argument('--run-id', help='Optional run directory identifier override.')
    parser.add_argument('--experiment-id', help='Optional experiment identifier for metadata.')
    parser.add_argument('--worker-id', type=int, help='Optional worker identifier for metadata.')
    parser.add_argument('--session-batch-id', type=int, help='Optional session batch identifier for metadata.')
    parser.add_argument('--site', help='Optional site override for auth refresh and metadata.')
    parser.add_argument('--task-variant', help='Optional task variant override for metadata.')
    parser.add_argument('--repeat-index', type=int, help='Optional repeat index for metadata.')
    parser.add_argument('--queue-index', type=int, help='Optional queue index for metadata.')
    parser.add_argument('--runs-root', help='Optional runs root override for output isolation.')
    parser.add_argument('--disable-schema-enhancement', action='store_true', help='Prevent browser-use from appending JSON schema text to compact prompts.')
    parser.add_argument('--prompt-footer-mode', choices=['full', 'omit-output-format'], default='full', help='Compatibility flag; Keyboard compact prompts do not include an Output Format footer.')
    parser.add_argument('--capture-structured-failures', action='store_true', help='Dump raw structured-output payloads on parse failures under the run directory.')
    parser.add_argument('--salvage-multi-json', action='store_true', help='Forward to the LLM wrapper to salvage the first valid JSON block on multi-JSON failures.')
    parser.add_argument('--enable-highlight-elements', action='store_true', help='Opt in to browser-use element highlights. Keyboard runs leave them disabled by default.')
    parser.add_argument('--disable-highlight-elements', action='store_true', help='Compatibility flag; Keyboard runs already disable highlights by default.')
    parser.add_argument('--current-focus-marker', action='store_true', help='Mark the current DOM focus in the existing text observation and screenshot.')
    parser.add_argument('--evidence-pack-manifest', help='Optional candidate-manifest.suspects.json for evidence-assisted observation markers.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task_path = resolve_task_path(args.task)
    if not task_path.exists():
        raise FileNotFoundError('Task file not found: ' + str(task_path))
    if args.print_prompt:
        task = load_task(task_path)
        prompt_text = build_task_prompt(task)
        evidence_pack_path = resolve_optional_path(args.evidence_pack_manifest)
        if evidence_pack_path is not None:
            evidence_pack = load_evidence_pack_manifest(
                evidence_pack_path,
                expected_task_id=task.task_id,
                expected_instance_id=task.instance_id,
                expected_family=task.issue_family,
            )
            prompt_text = append_evidence_pack_prompt(prompt_text, evidence_pack)
        print(prompt_text)
        return 0
    run_dir = asyncio.run(
        run_task(
            task_path=task_path,
            model=args.model,
            temperature=args.temperature,
            max_steps=args.max_steps,
            headless=args.headless,
            auth_state_override=args.auth_state_file,
            run_id=args.run_id,
            experiment_id=args.experiment_id,
            worker_id=args.worker_id,
            session_batch_id=args.session_batch_id,
            site=args.site,
            task_variant=args.task_variant,
            repeat_index=args.repeat_index,
            queue_index=args.queue_index,
            runs_root_override=args.runs_root,
            capture_structured_failures=args.capture_structured_failures,
            disable_schema_enhancement=args.disable_schema_enhancement,
            salvage_multi_json=args.salvage_multi_json,
            reasoning_effort=args.reasoning_effort,
            prompt_footer_mode=args.prompt_footer_mode,
            highlight_elements=args.enable_highlight_elements and not args.disable_highlight_elements,
            current_focus_marker=args.current_focus_marker,
            evidence_pack_manifest=args.evidence_pack_manifest,
        )
    )
    print('Run complete: ' + str(run_dir))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
