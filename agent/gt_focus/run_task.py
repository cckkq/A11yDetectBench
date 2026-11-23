#!/usr/bin/env python3
'''Focus GT task prompt and schema helpers.'''

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
    raise RuntimeError('PyYAML is required to load Focus GT task YAML files.') from exc


IssueFamily = Literal['visible_focus', 'focus_order', 'closing_content', 'modal_dialogs', 'revealing_content', 'focus_not_obscured']
SUPPORTED_ISSUE_TYPES = {'visible_focus', 'revealing_content'}
LEVEL3_ISSUE_FAMILY = 'focus_assessment_f1_to_f6'
ISSUE_TYPE_VALUES = ['visible_focus', 'focus_order', 'closing_content', 'modal_dialogs', 'revealing_content', 'focus_not_obscured']
GT_FOCUS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_FOCUS_DIR.parent.parent
BROWSER_USE_ROOT = PROJECT_ROOT.parent / 'browser-use'
TASKS_DIR = GT_FOCUS_DIR / 'tasks'
EVALUATE_RULES_DIR = GT_FOCUS_DIR / 'evaluate-rules'
RUNS_DIR = GT_FOCUS_DIR / 'runs'
CONVERSATION_CACHE_DIR = PROJECT_ROOT / 'agent' / '.conv'
BROWSER_RUNTIME_AUTH_DIR = GT_FOCUS_DIR / 'auth' / 'browser_runtime'
PASS_L1_PATCH_MANIFEST = GT_FOCUS_DIR / 'runtime_patches' / 'pass_l1_counterfactual.yaml'

if str(BROWSER_USE_ROOT) not in sys.path:
    sys.path.insert(0, str(BROWSER_USE_ROOT))

SELECTOR_FIELD_DESCRIPTION = 'verified CSS selector for the reported focus target, or empty string'
TARGET_FIELD_DESCRIPTION = 'natural-language description of the reported focus target'

VISIBLE_FOCUS_RULE = (
    'the component receives keyboard focus or becomes the keyboard-current item, but no '
    'user-perceivable focus indicator is visible in the rendered page state'
)
REVEALING_CONTENT_RULE = (
    'keyboard activation reveals hidden content, but focus does not move into the revealed content'
)
FOCUS_ORDER_RULE = (
    'components receive focus in an order that does not preserve meaning and operability'
)
CLOSING_CONTENT_RULE = (
    'closing revealed content does not move input focus to the component that revealed it'
)
MODAL_DIALOGS_RULE = (
    'users can Tab away from a modal dialog without explicitly dismissing it'
)
FOCUS_NOT_OBSCURED_RULE = (
    'the focus indicator for a keyboard-focused element is fully obscured by author-created overlaying content'
)
FOCUS_EVIDENCE_CONTRACT = (
    'For visible-focus checks, first show that real keyboard navigation placed focus on the target. '
    'Mouse clicks, JavaScript `.focus()`, and browser-use highlights or overlays do not prove focus or visible focus. '
    'Judge visible focus from the rendered page: the focused target must have a visible indication that lets a keyboard user tell where focus is. '
    'A selected or current style that was already visible, or a CSS change that is too subtle to see clearly, is not enough. '
    'Arrow keys are valid inside menus, tabs, listboxes, and similar widgets; if DOM focus stays on a container, identify the active item with aria-activedescendant or an equivalent current-item state.'
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
    return ' '.join(value.split())


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
    if family == 'visible_focus':
        return 'WCAG 2.4.7 focus-visible issue'
    if family == 'revealing_content':
        return 'WCAG 2.4.3 revealing-content focus issue'
    raise ValueError('Unsupported Focus issue_family: ' + family)


def _family_rule(family: str) -> str:
    if family == 'visible_focus':
        return VISIBLE_FOCUS_RULE
    if family == 'revealing_content':
        return REVEALING_CONTENT_RULE
    raise ValueError('Unsupported Focus issue_family: ' + family)


def build_task_prompt(task: TaskConfig) -> str:
    if _is_level_3(task):
        return build_level3_prompt(task)
    if _is_level_2(task):
        return build_level2_prompt(task)
    if task.issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Focus issue_family: ' + task.issue_family)

    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + ' for ' + _clean_text(task.wcag_target) + '.',
    ]
    if task.target_selector:
        chunks.append('Target selector: `' + _clean_text(task.target_selector) + '`')
    chunks.append('WCAG criterion: ' + _clean_text(task.wcag_clause_text))
    if task.setup:
        chunks.append(_sentence(task.setup))
    if task.issue_family == 'visible_focus':
        chunks.append('Use keyboard navigation to put focus on the target. Base the conclusion on the rendered page state while the target is actually keyboard-focused or keyboard-current.')
    else:
        chunks.append('Activate the target with the keyboard and inspect whether focus moves into the newly revealed content.')
    chunks.append('Report a ' + _issue_label(task.issue_family) + ' only if ' + _sentence(_family_rule(task.issue_family)))
    chunks.append(FOCUS_EVIDENCE_CONTRACT)
    chunks.append(_output_contract(task))
    return '\n\n'.join(chunks)


def build_level2_prompt(task: TaskConfig) -> str:
    if task.issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Focus issue_family: ' + task.issue_family)
    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + ' for ' + _clean_text(task.wcag_target) + '.',
        'WCAG criterion: ' + _clean_text(task.wcag_clause_text),
        'Report a ' + _issue_label(task.issue_family) + ' for each component where ' + _sentence(_family_rule(task.issue_family)),
        FOCUS_EVIDENCE_CONTRACT,
        _output_contract(task),
    ]
    return '\n\n'.join(chunks)


def build_level3_prompt(task: TaskConfig) -> str:
    if not task.wcag_criteria:
        raise ValueError('Level 3 Focus tasks require wcag_criteria')
    criteria_lines = ['WCAG criteria:']
    for label, criterion in task.wcag_criteria.items():
        criteria_lines.append(label + ' -> ' + _clean_text(criterion['target']) + ': ' + _clean_text(criterion['text']))
    chunks = [
        'Task: Inspect ' + _clean_text(task.target_description) + '.',
        '\n'.join(criteria_lines),
        'Report an issue for each component or focus interaction where either F.1 applies: ' + VISIBLE_FOCUS_RULE + '; or F.2 applies: ' + FOCUS_ORDER_RULE + '; or F.3 applies: ' + CLOSING_CONTENT_RULE + '; or F.4 applies: ' + MODAL_DIALOGS_RULE + '; or F.5 applies: ' + REVEALING_CONTENT_RULE + '; or F.6 applies: ' + FOCUS_NOT_OBSCURED_RULE + '.',
        FOCUS_EVIDENCE_CONTRACT,
        _output_contract(task),
    ]
    return '\n\n'.join(chunks)


def output_model_schema_for_task(task: TaskConfig) -> type[BaseModel]:
    if not _is_level_3(task) and task.issue_family in SUPPORTED_ISSUE_TYPES:
        return fixed_output_model_schema_for_family(task.issue_family, multi=is_multi_issue_task(task), output_format=task.output_format)
    if is_multi_issue_task(task):
        return multi_output_model_schema(output_format=task.output_format)
    return VerificationOutput


def _issue_output_format(output_format: dict[str, Any], multi: bool) -> dict[str, Any]:
    if multi:
        issues = output_format.get('issues')
        if isinstance(issues, list) and issues and isinstance(issues[0], dict):
            return issues[0]
        raise ValueError('Focus output_format.issues[0] must be present and must be a mapping.')
    return output_format


def _field_description(output_format: dict[str, Any], field_name: str) -> str:
    value = output_format.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError('Focus output_format.' + field_name + ' must be a non-empty string.')


def multi_output_model_schema(output_format: dict[str, Any] | None = None) -> type[BaseModel]:
    if output_format is None:
        raise ValueError('Focus output_format is required to build the output schema.')
    issue_format = _issue_output_format(output_format, multi=True)
    issue_model = create_model(
        'IssueOutput',
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


def fixed_output_model_schema_for_family(
    issue_family: str,
    multi: bool,
    output_format: dict[str, Any] | None = None,
) -> type[BaseModel]:
    if issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError('Unsupported Focus issue_family: ' + issue_family)
    if output_format is None:
        raise ValueError('Focus output_format is required to build the output schema.')
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
            'total_tokens': None,
            'reasoning_tokens': None,
            'estimated_cost_usd': None,
            'raw_usage': None,
        }
    raw_usage = usage.model_dump() if hasattr(usage, 'model_dump') else dict(usage)
    return {
        'usage_missing': False,
        'prompt_tokens': raw_usage.get('total_prompt_tokens'),
        'prompt_cached_tokens': raw_usage.get('total_prompt_cached_tokens'),
        'prompt_cache_creation_tokens': None,
        'prompt_image_tokens': None,
        'completion_tokens': raw_usage.get('total_completion_tokens'),
        'total_tokens': raw_usage.get('total_tokens'),
        'reasoning_tokens': None,
        'estimated_cost_usd': raw_usage.get('total_cost'),
        'raw_usage': raw_usage,
    }


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
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        suffix='.json',
        prefix='state_',
        dir=windows_long_path(runtime_dir),
        delete=False,
    ) as handle:
        json.dump(storage_state, handle, ensure_ascii=True, indent=2)
        handle.write('\n')
        return Path(handle.name)


def cleanup_runtime_storage_state_file(path: Path | None) -> None:
    if path is None:
        return
    safe_unlink(path)


def build_review_template(task: TaskConfig, evaluate_rule_path: Path | None) -> str:
    lines = [
        '# Manual Review: ' + task.task_id,
        '',
        '- instance_id: ' + task.instance_id,
        '- wcag_target: ' + task.wcag_target,
        '- modality_policy: ' + (task.modality_policy or ''),
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
    if '.' in task.instance_id:
        return task.instance_id.split('.', 1)[0]
    if '.' in task.task_id:
        return task.task_id.split('.', 1)[0]
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
        raise ValueError('Missing Focus PASS L1 runtime patch for ' + task.instance_id + ': ' + str(PASS_L1_PATCH_MANIFEST))
    if not isinstance(patch, dict):
        raise ValueError('Focus PASS L1 runtime patch must be a mapping for ' + task.instance_id)
    return patch


PASS_L1_PATCH_JS = r'''
(() => {
  const ID = __ID__;
  const SPEC = __SPEC__;
  const TASK_SELECTOR = __TARGET__;
  const selector = SPEC.selector || SPEC.trigger_selector || TASK_SELECTOR;
  const proxySelector = SPEC.proxy_selector || selector;
  const outline = SPEC.outline || '4px solid #d946ef';
  const outlineOffset = String(SPEC.outline_offset || '3px');
  const boxShadow = SPEC.box_shadow || '0 0 0 6px rgba(217,70,239,.28)';
  let started = false;
  let styleInstalled = false;
  const className = (() => {
    let hash = 0;
    for (let i = 0; i < ID.length; i += 1) hash = ((hash << 5) - hash + ID.charCodeAt(i)) | 0;
    return 'wa-kf-' + Math.abs(hash).toString(36);
  })();
  const esc = (value) => {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  };
  const installStyle = () => {
    if (styleInstalled) return true;
    const parent = document.head || document.documentElement;
    if (!parent) return false;
    const style = document.createElement('style');
    style.textContent = [
      `.${esc(className)} {`,
      `  outline: ${outline} !important;`,
      `  outline-offset: ${outlineOffset} !important;`,
      `  box-shadow: ${boxShadow} !important;`,
      '  background-color: rgba(217,70,239,.18) !important;',
      '}'
    ].join('\n');
    parent.appendChild(style);
    styleInstalled = true;
    return true;
  };
  const visible = (el) => {
    if (!el) return false;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const nodes = (sel) => {
    try { return Array.from(document.querySelectorAll(sel || '')); }
    catch (e) { return []; }
  };
  const styled = new Set();
  const clearStyled = () => {
    for (const el of Array.from(styled)) {
      el.classList.remove(className);
    }
    styled.clear();
  };
  const mark = (el) => {
    if (!el || !visible(el)) return false;
    el.classList.add(className);
    styled.add(el);
    return true;
  };
  const keyboardCurrent = (targetSelector) => {
    const targets = nodes(targetSelector).filter(visible);
    const active = document.activeElement;
    if (!active) return null;
    const direct = targets.find((el) => el === active || el.contains(active));
    if (direct) return direct;
    const activeId = active.getAttribute('aria-activedescendant');
    const activeDesc = activeId ? document.getElementById(activeId) : null;
    const byDesc = targets.find((el) => el === activeDesc || el.contains(activeDesc) || (activeDesc && activeDesc.contains(el)));
    if (byDesc) return byDesc;
    const role = (active.getAttribute('role') || '').toLowerCase();
    if (!['menu', 'menubar', 'listbox', 'tree', 'grid', 'tablist'].includes(role)) return null;
    return targets.find((el) => active.contains(el) && (el.classList.contains('ui-state-active') || el.getAttribute('aria-selected') === 'true')) || null;
  };
  const distance = (a, b) => {
    const ar = a.getBoundingClientRect();
    const br = b.getBoundingClientRect();
    const ax = ar.left + ar.width / 2;
    const ay = ar.top + ar.height / 2;
    const bx = br.left + br.width / 2;
    const by = br.top + br.height / 2;
    return Math.abs(ax - bx) + Math.abs(ay - by);
  };
  const targetProxy = (target) => {
    const proxies = nodes(proxySelector).filter(visible);
    if (!proxies.length) return null;
    const active = document.activeElement;
    const direct = proxies.find((el) => el === target || el.contains(target) || el === active || el.contains(active));
    if (direct) return direct;
    const adjacent = proxies.find((el) => el.previousElementSibling === target || el.nextElementSibling === target);
    if (adjacent) return adjacent;
    return proxies.slice().sort((a, b) => distance(a, target) - distance(b, target))[0] || target;
  };
  const triggerIsCurrent = () => {
    const triggerSelector = SPEC.trigger_selector || TASK_SELECTOR;
    const triggers = nodes(triggerSelector).filter(visible);
    const active = document.activeElement;
    return !!active && triggers.some((el) => el === active || el.contains(active));
  };
  const activationKeyMatches = (event) => {
    const keys = (SPEC.activation_keys || ['Enter', 'Space', 'ArrowDown']).map(String);
    return keys.includes(event.key) || (event.key === ' ' && keys.includes('Space')) || (event.key === 'Spacebar' && keys.includes('Space'));
  };
  const currentRevealedTarget = () => {
    const targets = nodes(SPEC.focus_target_selector || '').filter(visible);
    const active = document.activeElement;
    if (!active) return null;
    return targets.find((el) => el === active || el.contains(active)) || null;
  };
  const focusFirstRevealed = () => {
    const focusTarget = nodes(SPEC.focus_target_selector || '').filter(visible)[0];
    if (!focusTarget) return false;
    if (!focusTarget.hasAttribute('tabindex')) focusTarget.setAttribute('tabindex', '0');
    focusTarget.focus({preventScroll: false});
    return mark(focusTarget);
  };
  const scan = (reason) => {
    try {
      clearStyled();
      if (SPEC.kind === 'revealed_content_focus_shift') {
        const current = currentRevealedTarget();
        if (current) return mark(current);
        return reason === 'activation' ? focusFirstRevealed() : false;
      }
      const current = keyboardCurrent(selector);
      if (!current) return false;
      return mark(SPEC.kind === 'focus_within_proxy_style' ? targetProxy(current) : current);
    } catch (e) {
      clearStyled();
      return false;
    }
  };
  const start = () => {
    if (started) return;
    if (!installStyle()) return setTimeout(start, 0);
    started = true;
    document.addEventListener('focusin', () => scan('focusin'), true);
    document.addEventListener('keyup', () => scan('keyup'), true);
    document.addEventListener('keydown', (event) => {
      const reason = SPEC.kind === 'revealed_content_focus_shift' && activationKeyMatches(event) && triggerIsCurrent() ? 'activation' : 'keydown';
      setTimeout(() => scan(reason), 0);
    }, true);
    setTimeout(() => scan('start'), 0);
  };
  if (document.documentElement) start();
  else {
    document.addEventListener('DOMContentLoaded', start, {once: true});
    setTimeout(start, 0);
  }
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
    highlight_elements: bool = False,
    prompt_footer_mode: str = 'full',
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
            raise RuntimeError('Refreshed auth state failed probe for ' + auth_refresh_site + ': ' + probe_reason)
        auth_state_refreshed = True
    elif auth_state_override and auth_state_path is not None:
        if not auth_refresh_site:
            raise ValueError('Cannot infer site for auth probe: ' + task.task_id)
        probe_ok, probe_reason = await probe_task_auth_state(auth_refresh_site, auth_state_path)
        if not probe_ok:
            raise RuntimeError('Auth state override failed probe for ' + auth_refresh_site + ': ' + probe_reason)
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
        'highlight_elements': highlight_elements,
        'prompt_footer_mode': prompt_footer_mode,
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

        try:
            write_text(run_dir / 'task.prompt.txt.final', agent.task or '')
        except Exception:
            pass

        history = await agent.run(max_steps=max_steps)
        history.save_to_file(windows_long_path(run_dir / 'history.json'))
        write_json(run_dir / 'usage.json', build_usage_payload(history))

        final_result = history.final_result() or ''
        write_text(run_dir / 'final-response.txt', final_result)
        try:
            parsed_final = json.loads(final_result)
        except json.JSONDecodeError:
            parsed_final = {'raw': final_result}
        write_json(run_dir / 'final-response.json', parsed_final)

        meta.update(
            {
                'run_finished_at': datetime.now(timezone.utc).isoformat(),
                'agent_done': history.is_done(),
                'agent_success': history.is_successful(),
                'history_steps': len(history.history),
            }
        )
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
    parser = argparse.ArgumentParser(description='Run one Focus GT verification task with browser-use.')
    parser.add_argument('--task', required=True, help='Task file name under agent/gt_focus/tasks or a path.')
    parser.add_argument('--print-prompt', action='store_true', help='Print the compact agent-facing prompt and exit.')
    parser.add_argument('--model', default='gpt-5.2-20251211', help='LLM model name for browser-use execution.')
    parser.add_argument('--reasoning-effort', help='Optional reasoning effort for LLM routes that support it, e.g. Copilot.')
    parser.add_argument('--temperature', type=float, default=0, help='LLM temperature for verification runs.')
    parser.add_argument('--max-steps', type=int, default=25, help='Maximum browser-use agent steps.')
    parser.add_argument('--headless', action='store_true', help='Run the browser headlessly.')
    parser.add_argument('--auth-state-file', help='Optional auth state file override.')
    parser.add_argument('--run-id', help='Optional run directory identifier override.')
    parser.add_argument('--experiment-id', help='Optional experiment identifier for metadata.')
    parser.add_argument('--worker-id', type=int, help='Optional worker identifier for metadata.')
    parser.add_argument('--session-batch-id', type=int, help='Optional session batch identifier for metadata.')
    parser.add_argument('--site', help='Optional site override for metadata.')
    parser.add_argument('--task-variant', help='Optional task variant override for metadata.')
    parser.add_argument('--repeat-index', type=int, help='Optional repeat index for metadata.')
    parser.add_argument('--queue-index', type=int, help='Optional queue index for metadata.')
    parser.add_argument('--runs-root', help='Optional runs root override for output isolation.')
    parser.add_argument('--prompt-footer-mode', choices=['full', 'omit-output-format'], default='full', help='Compatibility flag; Focus compact prompts do not include an Output Format footer.')
    parser.add_argument('--disable-schema-enhancement', action='store_true', help='Prevent browser-use from appending JSON schema text to compact prompts.')
    parser.add_argument('--capture-structured-failures', action='store_true', help='Dump raw structured-output payloads on parse failures under the run directory.')
    parser.add_argument('--salvage-multi-json', action='store_true', help='Forward to the LLM wrapper to salvage the first valid JSON block on multi-JSON failures.')
    parser.add_argument('--enable-highlight-elements', action='store_true', help='Opt in to browser-use element highlights. Focus runs leave them disabled by default.')
    parser.add_argument('--disable-highlight-elements', action='store_true', help='Compatibility flag; Focus runs already disable highlights by default.')
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
            highlight_elements=args.enable_highlight_elements and not args.disable_highlight_elements,
            prompt_footer_mode=args.prompt_footer_mode,
            current_focus_marker=args.current_focus_marker,
            evidence_pack_manifest=args.evidence_pack_manifest,
        )
    )
    print('Run complete: ' + str(run_dir))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
