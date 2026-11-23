#!/usr/bin/env python3
"""Run one ERROR GT verification task with browser-use.

ERROR tasks use the same strict-runner shape as Links: compact prompts stay
agent-facing, while task metadata, output schema, runtime patches, and evaluator
gold evidence remain runner configuration.
"""

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
from agent.gt.path_utils import safe_copy2, safe_mkdir, safe_unlink, windows_long_path, write_json_file, write_text_file

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError("PyYAML is required to load ERROR GT task YAML files.") from exc


GT_ERRORS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_ERRORS_DIR.parent.parent
BROWSER_USE_ROOT = PROJECT_ROOT.parent / "browser-use"
GENERATED_SELECTED_DIR = GT_ERRORS_DIR / "generated_clean_pilot" / "generated"
TASKS_DIR = GENERATED_SELECTED_DIR / "tasks"
EVALUATE_RULES_DIR = GENERATED_SELECTED_DIR / "evaluate-rules"
RUNS_DIR = GT_ERRORS_DIR / "runs"
CONVERSATION_CACHE_DIR = PROJECT_ROOT / "agent" / ".conv"
BROWSER_RUNTIME_AUTH_DIR = GT_ERRORS_DIR / "auth" / "browser_runtime"
PASS_L1_PATCH_MANIFEST = GT_ERRORS_DIR / "runtime_patches" / "pass_l1_counterfactual.yaml"


IssueFamily = Literal["error_identification", "error_suggestion", "error_prevention", "status_messages"]
SUPPORTED_ISSUE_TYPES = {"error_identification", "error_suggestion", "error_prevention", "status_messages"}
LEVEL3_ISSUE_FAMILY = "error_assessment_e1_to_e4"
ISSUE_TYPE_VALUES = ["error_identification", "error_suggestion", "error_prevention", "status_messages"]
SELECTOR_FIELD_DESCRIPTION = "verified CSS selector for the field/control path where the issue belongs"
TARGET_FIELD_DESCRIPTION = "natural-language description of the field/control path where the issue belongs"
TARGET_REPORTING_POLICY = (
    "Do not report the rendered status/error/progress message node, or the submit button "
    "when the issue belongs to a field/control."
)


class VerificationOutput(BaseModel):
    verdict: Literal["issue_found", "no_issue_found"]
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
    verdict: Literal["issue_found", "no_issue_found"]
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
    probe: str | None = None
    task_type: str = "verification"
    evaluate_rule_file: str | None = None
    difficulty: str | None = None
    issue_domain: str | None = None
    modality_policy: str | None = None
    auth_state_file: str | None = None
    wcag_source_url: str | None = None
    setup: str | None = None
    wcag_criteria: dict[str, dict[str, str]] | None = None
    output_format: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "TaskConfig":
        return cls(**data)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def load_task(path: Path) -> TaskConfig:
    return TaskConfig.from_mapping(load_yaml(path))


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _sentence(value: str) -> str:
    value = _clean_text(value)
    if value.endswith((".", "?", "!")):
        return value
    return f"{value}."


def _inline_probe(value: str) -> str:
    value = _sentence(value)
    if value and value[0].isalpha():
        value = value[0].lower() + value[1:]
    return value


def _issue_label(task: TaskConfig) -> str:
    if task.issue_family == "error_identification":
        return "WCAG 3.3.1 error-identification issue"
    if task.issue_family == "error_suggestion":
        return "WCAG 3.3.3 error-suggestion issue"
    if task.issue_family == "error_prevention":
        return "WCAG 3.3.4 error-prevention issue"
    if task.issue_family == "status_messages":
        return "WCAG 4.1.3 status-messages issue"
    raise ValueError(f"Unsupported Error issue_family: {task.issue_family}")


def _shared_rule(task: TaskConfig) -> str:
    if task.issue_family == "error_identification":
        return (
            "the target path has an automatically detected input error and the page does not "
            "identify the item that is in error or describe the error to the user"
        )
    if task.issue_family == "error_suggestion":
        return (
            "the target path has an automatically detected input error and the page does not "
            "provide an actionable correction suggestion"
        )
    if task.issue_family == "error_prevention":
        return (
            "the target submission may have serious consequences and does not provide a reversible "
            "submission, input-error checking with an opportunity to correct, or a review/confirm/correct "
            "step before finalizing the submission"
        )
    if task.issue_family == "status_messages":
        return (
            "the target interaction triggers an active same-page status message and that message "
            "is not programmatically exposed through role, aria-live, or equivalent status-message semantics"
        )
    raise ValueError(f"Unsupported Error issue_family: {task.issue_family}")


def _level2_rule(task: TaskConfig) -> str:
    return _shared_rule(task)


def _is_level_2(task: TaskConfig) -> bool:
    return task.difficulty == "level_2_clause_given_location_hidden" or task.task_id.endswith(".level2.v1")


def _is_level_3(task: TaskConfig) -> bool:
    return task.issue_family == LEVEL3_ISSUE_FAMILY or task.task_id.endswith(".level3.v1")


def is_multi_issue_task(task: TaskConfig) -> bool:
    return isinstance(task.output_format.get("issues"), list) or _is_level_2(task) or _is_level_3(task)


def _output_contract(task: TaskConfig) -> str:
    if is_multi_issue_task(task):
        return "Report only issues that are present. If no issues are present, use verdict `no_issue_found` and leave the `issues` list empty."
    return "If the issue is present, use verdict `issue_found`; otherwise use verdict `no_issue_found`."


def _target_reporting_policy() -> str:
    return TARGET_REPORTING_POLICY


def build_level2_prompt(task: TaskConfig) -> str:
    chunks = [
        f"Task: Inspect {_clean_text(task.target_description)} for {_clean_text(task.wcag_target)}.",
        f"WCAG criterion: {_clean_text(task.wcag_clause_text)}",
    ]
    if task.setup:
        chunks.append(_sentence(task.setup))
    target_kind = "target interaction" if task.issue_family == "status_messages" else "target path"
    chunks.append(
        "Report a "
        f"{_issue_label(task)} for each {target_kind} where "
        f"{_sentence(_level2_rule(task))}"
    )
    chunks.append(_target_reporting_policy())
    chunks.append(_output_contract(task))
    return "\n\n".join(chunks)


def build_level3_prompt(task: TaskConfig) -> str:
    if not task.wcag_criteria:
        raise ValueError("Level 3 ERROR tasks require wcag_criteria")
    criteria_lines = ["WCAG criteria:"]
    for label, criterion in task.wcag_criteria.items():
        criteria_lines.append(
            f"{label} -> {_clean_text(criterion['target'])}: {_clean_text(criterion['text'])}"
        )
    chunks = [
        f"Task: Inspect {_clean_text(task.target_description)}.",
        "\n".join(criteria_lines),
    ]
    if task.setup:
        chunks.append(_sentence(task.setup))
    chunks.append(
        "Report an issue for each target interaction, input-error path, or serious-consequence "
        "submission path where either E.1 applies: "
        "the target path has an automatically detected input error and the page does not identify "
        "the item that is in error or describe the error to the user; or E.2 applies: "
        "the target path has an automatically detected input error and the page does not provide "
        "an actionable correction suggestion; or E.3 applies: the target submission allows users "
        "to make legal commitments or financial transactions, modify or delete data in a data "
        "storage system, or submit test responses, but does not provide a reversible submission, "
        "input-error checking with an opportunity to correct, or a review/confirm/correct step "
        "before finalizing the submission; or E.4 applies: the target interaction triggers an "
        "active same-page status message and that message is not programmatically exposed through "
        "role, aria-live, or equivalent status-message semantics."
    )
    chunks.append(_target_reporting_policy())
    chunks.append(_output_contract(task))
    return "\n\n".join(chunks)


def build_task_prompt(task: TaskConfig) -> str:
    if _is_level_3(task):
        return build_level3_prompt(task)

    if task.issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError(f"Unsupported Error issue_family: {task.issue_family}")

    if _is_level_2(task):
        return build_level2_prompt(task)

    task_line = f"Task: Inspect {_clean_text(task.target_description)} for {_clean_text(task.wcag_target)}."
    if task.probe:
        task_line = f"{task_line} For this target, {_inline_probe(task.probe)}"

    chunks = [task_line]
    if task.target_selector:
        chunks.append(f"Target selector: `{_clean_text(task.target_selector)}`")
    chunks.append(f"WCAG criterion: {_clean_text(task.wcag_clause_text)}")
    if task.setup:
        chunks.append(_sentence(task.setup))
    chunks.append(f"Report a {_issue_label(task)} only if {_sentence(_shared_rule(task))}")
    chunks.append(_target_reporting_policy())
    chunks.append(_output_contract(task))
    return "\n\n".join(chunks)


def output_model_schema_for_task(task: TaskConfig) -> type[BaseModel]:
    if not _is_level_3(task) and task.issue_family in SUPPORTED_ISSUE_TYPES:
        return fixed_output_model_schema_for_family(
            task.issue_family,
            multi=is_multi_issue_task(task),
            output_format=task.output_format,
        )
    if is_multi_issue_task(task):
        return multi_output_model_schema(output_format=task.output_format)
    return VerificationOutput


def _issue_output_format(output_format: dict[str, Any], multi: bool) -> dict[str, Any]:
    if multi:
        issues = output_format.get("issues")
        if isinstance(issues, list) and issues and isinstance(issues[0], dict):
            return issues[0]
        raise ValueError("ERROR output_format.issues[0] must be present and must be a mapping.")
    return output_format


def _field_description(output_format: dict[str, Any], field_name: str) -> str:
    value = output_format.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"ERROR output_format.{field_name} must be a non-empty string.")


def multi_output_model_schema(output_format: dict[str, Any] | None = None) -> type[BaseModel]:
    if output_format is None:
        raise ValueError("ERROR output_format is required to build the output schema.")
    issue_format = _issue_output_format(output_format, multi=True)
    issue_model = create_model(
        "ErrorIssueOutput",
        selector=(str, Field(..., description=_field_description(issue_format, "selector"))),
        target=(str, Field(..., description=_field_description(issue_format, "target"))),
        issue_type=(IssueFamily, Field(..., description=_field_description(issue_format, "issue_type"))),
        observed_behavior=(str, Field(..., description=_field_description(issue_format, "observed_behavior"))),
        evidence=(str, Field(..., description=_field_description(issue_format, "evidence"))),
    )
    return create_model(
        "MultiIssueVerificationOutput",
        verdict=(Literal["issue_found", "no_issue_found"], Field(..., description=_field_description(output_format, "verdict"))),
        issues=(list[issue_model], ...),
    )


def fixed_output_model_schema_for_family(
    issue_family: str,
    multi: bool,
    output_format: dict[str, Any] | None = None,
) -> type[BaseModel]:
    if issue_family not in SUPPORTED_ISSUE_TYPES:
        raise ValueError(f"Unsupported Error issue_family: {issue_family}")
    if output_format is None:
        raise ValueError("ERROR output_format is required to build the output schema.")
    issue_format = _issue_output_format(output_format, multi=multi)
    issue_model = create_model(
        f"ErrorIssueOutput_{issue_family}",
        selector=(str, Field(..., description=_field_description(issue_format, "selector"))),
        target=(str, Field(..., description=_field_description(issue_format, "target"))),
        issue_type=(Literal[issue_family], Field(..., description=_field_description(issue_format, "issue_type"))),
        observed_behavior=(str, Field(..., description=_field_description(issue_format, "observed_behavior"))),
        evidence=(str, Field(..., description=_field_description(issue_format, "evidence"))),
    )
    if multi:
        return create_model(
            f"ErrorMultiIssueVerificationOutput_{issue_family}",
            verdict=(Literal["issue_found", "no_issue_found"], Field(..., description=_field_description(output_format, "verdict"))),
            issues=(list[issue_model], ...),
        )
    return create_model(
        f"ErrorVerificationOutput_{issue_family}",
        verdict=(Literal["issue_found", "no_issue_found"], Field(..., description=_field_description(output_format, "verdict"))),
        selector=(str, Field(..., description=_field_description(output_format, "selector"))),
        target=(str, Field(..., description=_field_description(output_format, "target"))),
        issue_type=(Literal[issue_family], Field(..., description=_field_description(output_format, "issue_type"))),
        observed_behavior=(str, Field(..., description=_field_description(output_format, "observed_behavior"))),
        evidence=(str, Field(..., description=_field_description(output_format, "evidence"))),
    )


def resolve_task_path(task_arg: str) -> Path:
    candidate = Path(task_arg)
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
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
    if os.name != "nt":
        return run_dir / "conversation"
    token = hashlib.sha1(str(run_dir).encode("utf-8")).hexdigest()[:16]
    return CONVERSATION_CACHE_DIR / token


def build_task_output_dir_name(task_id: str) -> str:
    if os.name != "nt":
        return task_id

    parts = task_id.split(".")
    prefix = ".".join(parts[:3]) if len(parts) >= 3 else task_id[:24]
    if len(prefix) > 40 and len(parts) >= 2:
        prefix = ".".join(parts[:2])
    if len(prefix) > 40:
        prefix = prefix[:40]

    if task_id.endswith(".verify.level3.v1"):
        variant = "verify_l3_v1"
    elif task_id.endswith(".verify.level2.v1"):
        variant = "verify_l2_v1"
    elif task_id.endswith(".verify.v1"):
        variant = "verify_v1"
    else:
        variant = "_".join(parts[-3:]).replace("level", "l")

    digest = hashlib.sha1(task_id.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}.{variant}.{digest}"


def resolve_evaluate_rule(task_path: Path, task: TaskConfig) -> Path | None:
    explicit = resolve_optional_path(task.evaluate_rule_file)
    if explicit is not None and explicit.exists():
        return explicit
    by_name = EVALUATE_RULES_DIR / task_path.name
    if by_name.exists():
        return by_name
    by_task_id = EVALUATE_RULES_DIR / f"{task.task_id}.yaml"
    if by_task_id.exists():
        return by_task_id
    return None


def write_json(path: Path, payload: Any) -> None:
    write_json_file(path, payload)


def write_text(path: Path, text: str) -> None:
    write_text_file(path, text)


def build_usage_payload(history: Any) -> dict[str, Any]:
    usage = getattr(history, "usage", None)
    if usage is None:
        return {
            "usage_missing": True,
            "prompt_tokens": None,
            "prompt_cached_tokens": None,
            "prompt_cache_creation_tokens": None,
            "prompt_image_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "reasoning_tokens": None,
            "estimated_cost_usd": None,
            "raw_usage": None,
        }

    raw_usage = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)
    return {
        "usage_missing": False,
        "prompt_tokens": raw_usage.get("total_prompt_tokens"),
        "prompt_cached_tokens": raw_usage.get("total_prompt_cached_tokens"),
        "prompt_cache_creation_tokens": None,
        "prompt_image_tokens": None,
        "completion_tokens": raw_usage.get("total_completion_tokens"),
        "total_tokens": raw_usage.get("total_tokens"),
        "reasoning_tokens": None,
        "estimated_cost_usd": raw_usage.get("total_cost"),
        "raw_usage": raw_usage,
    }


def load_storage_state(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Auth state file is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Auth state file must contain a JSON object: {path}")
    return payload


def create_runtime_storage_state_file(storage_state: dict[str, Any] | None, run_dir: Path) -> Path | None:
    if storage_state is None:
        return None
    token = hashlib.sha1(str(run_dir.resolve(strict=False)).encode("utf-8")).hexdigest()[:16]
    runtime_dir = BROWSER_RUNTIME_AUTH_DIR / token
    safe_mkdir(runtime_dir)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        prefix="state_",
        dir=windows_long_path(runtime_dir),
        delete=False,
    ) as handle:
        json.dump(storage_state, handle, ensure_ascii=True, indent=2)
        handle.write("\n")
        return Path(handle.name)


def cleanup_runtime_storage_state_file(path: Path | None) -> None:
    if path is None:
        return
    safe_unlink(path)


def build_review_template(task: TaskConfig, evaluate_rule_path: Path | None) -> str:
    lines = [
        f"# Manual Review: {task.task_id}",
        "",
        f"- instance_id: {task.instance_id}",
        f"- wcag_target: {task.wcag_target}",
        f"- modality_policy: {task.modality_policy or ''}",
        f"- evaluate_rule: {evaluate_rule_path if evaluate_rule_path else 'N/A'}",
        "",
        "## Review",
        "- verdict_correct: ",
        "- target_correct: ",
        "- behavior_correct: ",
        "- overall: ",
        "",
        "## Notes",
        "- ",
    ]
    return "\n".join(lines)


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
    if "." in task.instance_id:
        return task.instance_id.split(".", 1)[0]
    if "." in task.task_id:
        return task.task_id.split(".", 1)[0]
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


PASS_L1_PATCH_JS = r'''
(() => {
  const ID = __ID__;
  const SPEC = __SPEC__;
  const TARGET_SELECTOR = __TARGET__;
  const touched = new WeakSet();
  const logs = [];
  const errors = [];
  let observerStarted = false;
  let generatedMessage = null;
  const textOf = (el) => ((el && (el.innerText || el.textContent)) || '').replace(/\s+/g, ' ').trim();
  const log = (reason, el) => {
    const item = {
      id: ID,
      reason,
      text: textOf(el).slice(0, 240),
      tag: el && el.tagName,
      cls: el && typeof el.className === 'string' ? el.className : '',
      ts: Date.now(),
    };
    logs.push(item);
    if (logs.length > 160) logs.splice(0, logs.length - 160);
  };
  const mark = (el, reason) => {
    if (!el || el.nodeType !== 1) return false;
    touched.add(el);
    log(reason, el);
    return true;
  };
  const applyLive = (el, reason) => {
    if (!el || el.nodeType !== 1) return false;
    const role = SPEC.role || 'alert';
    const live = SPEC.live || (role === 'alert' ? 'assertive' : 'polite');
    const txt = textOf(el);
    if (SPEC.match && !txt.includes(SPEC.match) && SPEC.selector !== '.loading-mask') return false;
    if (el.getAttribute('role') === role && el.getAttribute('aria-live') === live && el.getAttribute('aria-atomic') === 'true') return false;
    el.setAttribute('role', role);
    el.setAttribute('aria-live', live);
    el.setAttribute('aria-atomic', 'true');
    mark(el, reason);
    return true;
  };
  const patchAppendHint = () => {
    let count = 0;
    for (const el of document.querySelectorAll(SPEC.selector || '')) {
      const txt = textOf(el);
      if (!txt.includes(SPEC.match || '') && !txt.includes(SPEC.hint || '')) continue;
      if (SPEC.hint && !txt.includes(SPEC.hint)) {
        const span = document.createElement('span');
        span.textContent = SPEC.hint;
        span.style.display = 'block';
        touched.add(span);
        el.appendChild(span);
      }
      if (mark(el, 'append_hint')) count++;
    }
    return count;
  };
  const patchReplaceText = () => {
    let count = 0;
    for (const el of document.querySelectorAll(SPEC.selector || '')) {
      const txt = textOf(el);
      if (!txt.includes(SPEC.match || '') && !txt.includes(SPEC.text || '')) continue;
      if (txt !== SPEC.text) el.textContent = SPEC.text;
      if (mark(el, 'replace_text')) count++;
    }
    return count;
  };
  const patchLiveSelector = () => {
    let count = 0;
    for (const el of document.querySelectorAll(SPEC.selector || '')) {
      if (applyLive(el, 'live_selector')) count++;
    }
    return count;
  };
  const patchLiveText = () => {
    let count = 0;
    const nodes = Array.from(document.querySelectorAll('div,p,span,li,td,section,ul'))
      .filter((el) => textOf(el).includes(SPEC.match || ''))
      .sort((a, b) => textOf(a).length - textOf(b).length)
      .slice(0, 4);
    for (const el of nodes) {
      if (applyLive(el, 'live_text')) count++;
    }
    return count;
  };
  const ensureMessage = (kind) => {
    let msg = generatedMessage && document.contains(generatedMessage) ? generatedMessage : null;
    if (!msg) {
      msg = document.createElement('div');
      msg.id = 'status-message-' + Math.random().toString(36).slice(2, 10);
      msg.className = 'message message-error error';
      msg.textContent = SPEC.text;
      msg.style.margin = '10px 0';
      msg.style.padding = '12px';
      msg.style.border = '2px solid #b91c1c';
      msg.style.background = '#fee2e2';
      const anchor = document.querySelector('.page-main-actions, .page-title-wrapper, h1, main, body');
      if (anchor && anchor.parentNode && anchor !== document.body) anchor.parentNode.insertBefore(msg, anchor.nextSibling);
      else document.body.insertBefore(msg, document.body.firstChild);
      generatedMessage = msg;
    }
    mark(msg, kind);
    try {
      for (const input of document.querySelectorAll(TARGET_SELECTOR || '')) {
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', msg.id);
      }
    } catch (e) {}
    return 1;
  };
  const scan = () => {
    try {
      if (SPEC.kind === 'append_hint') return patchAppendHint();
      if (SPEC.kind === 'replace_text') return patchReplaceText();
      if (SPEC.kind === 'live_selector') return patchLiveSelector();
      if (SPEC.kind === 'live_text') return patchLiveText();
      if (SPEC.kind === 'grid_message') return ensureMessage('grid_message');
      if (SPEC.kind === 'report_intercept') return ensureMessage('report_intercept');
    } catch (e) {
      errors.push(String(e && e.message || e));
      if (errors.length > 40) errors.splice(0, errors.length - 40);
    }
    return 0;
  };
  const start = () => {
    scan();
    if (!observerStarted) {
      observerStarted = true;
      new MutationObserver(() => scan()).observe(document.documentElement, {subtree: true, childList: true, characterData: true});
      let n = 0;
      const timer = setInterval(() => { scan(); if (++n > 1200) clearInterval(timer); }, 100);
    }
  };
  const wait = () => document.documentElement ? start() : setTimeout(wait, 0);
  wait();
})();
'''


def load_pass_l1_patch_manifest() -> dict[str, Any]:
    if not PASS_L1_PATCH_MANIFEST.exists():
        return {}
    manifest = load_yaml(PASS_L1_PATCH_MANIFEST)
    patches = manifest.get("patches") or {}
    if not isinstance(patches, dict):
        raise ValueError(f"patches must be a mapping: {PASS_L1_PATCH_MANIFEST}")
    return patches


def is_generated_pass_task(task_path: Path, task: TaskConfig) -> bool:
    joined = "/".join(part.lower() for part in task_path.parts)
    if "generated_pass" in joined:
        return True
    return bool(task.evaluate_rule_file and "generated_pass" in task.evaluate_rule_file.lower())


def pass_l1_patch_for_task(task_path: Path, task: TaskConfig) -> dict[str, Any] | None:
    if not is_generated_pass_task(task_path, task):
        return None
    patches = load_pass_l1_patch_manifest()
    patch = patches.get(task.instance_id)
    if patch is None:
        raise ValueError(f"Missing PASS L1 runtime patch for {task.instance_id}: {PASS_L1_PATCH_MANIFEST}")
    if not isinstance(patch, dict):
        raise ValueError(f"PASS L1 runtime patch must be a mapping for {task.instance_id}")
    return patch


def make_pass_l1_patch_script(task: TaskConfig, patch_spec: dict[str, Any]) -> str:
    return (
        PASS_L1_PATCH_JS.replace("__ID__", json.dumps(task.instance_id))
        .replace("__SPEC__", json.dumps(patch_spec))
        .replace("__TARGET__", json.dumps(task.target_selector or ""))
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
    prompt_footer_mode: str = "full",
) -> Path:
    task = load_task(task_path)
    evaluate_rule_path = resolve_evaluate_rule(task_path, task)
    auth_state_path = resolve_optional_path(auth_state_override) if auth_state_override else resolve_optional_path(task.auth_state_file)
    runs_root = resolve_runs_root(runs_root_override)
    patch_spec = pass_l1_patch_for_task(task_path, task)

    if auth_state_override and auth_state_path is not None and not auth_state_path.exists():
        raise FileNotFoundError(f"Auth state file not found: {auth_state_path}")

    run_dir_name = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = runs_root / build_task_output_dir_name(task.task_id) / run_dir_name
    conversation_dir = build_conversation_dir(run_dir)
    safe_mkdir(run_dir)
    safe_mkdir(conversation_dir)

    auth_state_refreshed = False
    auth_refresh_site = infer_site_from_task(task, site_override=site)
    if task.auth_state_file and not auth_state_override:
        if not auth_refresh_site:
            raise ValueError(f"Cannot infer site for auth refresh: {task.task_id}")
        refreshed_auth_path = run_dir / "refreshed_auth.storage_state.json"
        auth_state_path = await refresh_task_auth_state(auth_refresh_site, refreshed_auth_path, headless=True)
        probe_ok, probe_reason = await probe_task_auth_state(auth_refresh_site, auth_state_path)
        if not probe_ok:
            raise RuntimeError(f"Refreshed auth state failed probe for {auth_refresh_site}: {probe_reason}")
        auth_state_refreshed = True
    elif auth_state_override and auth_state_path is not None:
        if not auth_refresh_site:
            raise ValueError(f"Cannot infer site for auth probe: {task.task_id}")
        probe_ok, probe_reason = await probe_task_auth_state(auth_refresh_site, auth_state_path)
        if not probe_ok:
            raise RuntimeError(f"Auth state override failed probe for {auth_refresh_site}: {probe_reason}")
    elif auth_state_path is not None and not auth_state_path.exists():
        raise FileNotFoundError(f"Auth state file not found: {auth_state_path}")

    safe_copy2(task_path, run_dir / "task.snapshot.yaml")
    if evaluate_rule_path is not None:
        safe_copy2(evaluate_rule_path, run_dir / "evaluate-rule.snapshot.yaml")

    prompt_text = build_task_prompt(task)
    write_text(run_dir / "task.prompt.txt", prompt_text)
    write_text(run_dir / "review.template.md", build_review_template(task, evaluate_rule_path))
    write_text(run_dir / "conversation.path.txt", str(conversation_dir))

    previous_structured_debug_dir = os.environ.get("BROWSER_USE_STRUCTURED_DEBUG_DIR")
    if capture_structured_failures:
        structured_debug_dir = run_dir / "spf"
        safe_mkdir(structured_debug_dir)
        os.environ["BROWSER_USE_STRUCTURED_DEBUG_DIR"] = str(structured_debug_dir)

    AgentClass, BrowserSessionClass = get_browser_use_classes()
    original_schema_enhancer = None
    if disable_schema_enhancement:
        original_schema_enhancer = getattr(AgentClass, "_enhance_task_with_schema", None)
        AgentClass._enhance_task_with_schema = lambda self, task, schema: task

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
        "task_id": task.task_id,
        "instance_id": task.instance_id,
        "task_file": str(task_path),
        "evaluate_rule_file": str(evaluate_rule_path) if evaluate_rule_path else None,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "temperature": temperature,
        "max_steps": max_steps,
        "headless": headless,
        "start_url": task.start_url,
        "run_started_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_dir_name,
        "experiment_id": experiment_id,
        "worker_id": worker_id,
        "session_batch_id": session_batch_id,
        "site": site,
        "task_variant": task_variant,
        "repeat_index": repeat_index,
        "queue_index": queue_index,
        "auth_state_file": str(auth_state_path) if auth_state_path else None,
        "auth_state_refreshed": auth_state_refreshed,
        "auth_refresh_site": auth_refresh_site,
        "runs_root": str(runs_root),
        "conversation_dir": str(conversation_dir),
        "capture_structured_failures": capture_structured_failures,
        "disable_schema_enhancement": disable_schema_enhancement,
        "salvage_multi_json": salvage_multi_json,
        "highlight_elements": highlight_elements,
        "prompt_footer_mode": prompt_footer_mode,
        "runtime_patch_applied": bool(patch_spec),
        "runtime_patch_manifest": str(PASS_L1_PATCH_MANIFEST) if patch_spec else None,
    }
    write_json(run_dir / "meta.json", meta)

    try:
        browser_session = BrowserSessionClass(
            headless=headless,
            storage_state=browser_storage_state_path,
            viewport={"width": 1280, "height": 900},
            window_size={"width": 1280, "height": 900},
            enable_default_extensions=False,
            highlight_elements=highlight_elements,
            dom_highlight_elements=False,
        )
        if hasattr(browser_session, "start"):
            await browser_session.start()
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
            generate_gif=str(run_dir / "recording.gif"),
            directly_open_url=False,
            initial_actions=[{"navigate": {"url": task.start_url, "new_tab": False}}],
        )

        try:
            write_text(run_dir / "task.prompt.txt.final", agent.task or "")
        except Exception:
            pass

        history = await agent.run(max_steps=max_steps)
        history.save_to_file(windows_long_path(run_dir / "history.json"))
        write_json(run_dir / "usage.json", build_usage_payload(history))

        final_result = history.final_result() or ""
        write_text(run_dir / "final-response.txt", final_result)
        try:
            parsed_final = json.loads(final_result)
        except json.JSONDecodeError:
            parsed_final = {"raw": final_result}
        write_json(run_dir / "final-response.json", parsed_final)

        meta.update(
            {
                "run_finished_at": datetime.now(timezone.utc).isoformat(),
                "agent_done": history.is_done(),
                "agent_success": history.is_successful(),
                "history_steps": len(history.history),
            }
        )
        write_json(run_dir / "meta.json", meta)
        return run_dir
    finally:
        if capture_structured_failures:
            if previous_structured_debug_dir is None:
                os.environ.pop("BROWSER_USE_STRUCTURED_DEBUG_DIR", None)
            else:
                os.environ["BROWSER_USE_STRUCTURED_DEBUG_DIR"] = previous_structured_debug_dir
        if disable_schema_enhancement and original_schema_enhancer is not None:
            AgentClass._enhance_task_with_schema = original_schema_enhancer
        await cleanup_browser_session(browser_session)
        cleanup_runtime_storage_state_file(browser_storage_state_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one ERROR GT verification task with browser-use.")
    parser.add_argument(
        "--task",
        required=True,
        help="Task file name under agent/gt_errors/generated_clean_pilot/generated/tasks or a path.",
    )
    parser.add_argument("--print-prompt", action="store_true", help="Print the compact agent-facing prompt and exit.")
    parser.add_argument("--model", default="gpt-5.2-20251211", help="LLM model name for browser-use execution.")
    parser.add_argument("--reasoning-effort", help="Optional reasoning effort for LLM routes that support it, e.g. Copilot.")
    parser.add_argument("--temperature", type=float, default=0, help="LLM temperature for verification runs.")
    parser.add_argument("--max-steps", type=int, default=25, help="Maximum browser-use agent steps.")
    parser.add_argument("--headless", action="store_true", help="Run the browser headlessly.")
    parser.add_argument("--auth-state-file", help="Optional auth state file override.")
    parser.add_argument("--run-id", help="Optional run directory identifier override.")
    parser.add_argument("--experiment-id", help="Optional experiment identifier for metadata.")
    parser.add_argument("--worker-id", type=int, help="Optional worker identifier for metadata.")
    parser.add_argument("--session-batch-id", type=int, help="Optional session batch identifier for metadata.")
    parser.add_argument("--site", help="Optional site override for metadata.")
    parser.add_argument("--task-variant", help="Optional task variant override for metadata.")
    parser.add_argument("--repeat-index", type=int, help="Optional repeat index for metadata.")
    parser.add_argument("--queue-index", type=int, help="Optional queue index for metadata.")
    parser.add_argument("--runs-root", help="Optional runs root override for output isolation.")
    parser.add_argument(
        "--prompt-footer-mode",
        choices=["full", "omit-output-format"],
        default="full",
        help="Compatibility flag; ERROR compact prompts do not include an Output Format footer.",
    )
    parser.add_argument(
        "--disable-schema-enhancement",
        action="store_true",
        help="Prevent browser-use from appending JSON schema text to compact prompts.",
    )
    parser.add_argument(
        "--capture-structured-failures",
        action="store_true",
        help="Dump raw structured-output payloads on parse failures under the run directory.",
    )
    parser.add_argument(
        "--salvage-multi-json",
        action="store_true",
        help="Forward to the LLM wrapper to salvage the first valid JSON block on multi-JSON failures.",
    )
    parser.add_argument(
        "--enable-highlight-elements",
        action="store_true",
        help="Opt in to browser-use element highlights. ERROR runs leave them disabled by default.",
    )
    parser.add_argument(
        "--disable-highlight-elements",
        action="store_true",
        help="Compatibility flag; ERROR runs already disable highlights by default.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task_path = resolve_task_path(args.task)
    if not task_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_path}")

    if args.print_prompt:
        print(build_task_prompt(load_task(task_path)))
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
        )
    )
    print(f"Run complete: {run_dir}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
