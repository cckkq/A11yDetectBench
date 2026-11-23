#!/usr/bin/env python3
"""Rule-based evaluator for one completed Links GT run.

The evaluator is intentionally conservative. For the current generated-clean
pilot it supports one gold target per evaluate-rule and checks whether the
agent's selector resolves inside that gold target set. Multi-issue outputs
are handled by searching all issues for a matching gold target.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
import hashlib
from pathlib import Path
from typing import Any

from agent.gt.path_utils import safe_mkdir, write_json_file

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError("PyYAML is required to load Links evaluate-rule snapshots.") from exc


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GT_LINKS_DIR = Path(__file__).resolve().parent
EVAL_AUTH_RUNTIME_DIR = GT_LINKS_DIR / "auth" / "eval_auth"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_json_file(path, payload)


def eval_auth_state_path_for_run(run_dir: Path, site: str) -> Path:
    token = hashlib.sha1(str(run_dir.resolve(strict=False)).encode("utf-8")).hexdigest()[:16]
    return EVAL_AUTH_RUNTIME_DIR / site / token / "eval_auth.storage_state.json"


def resolve_path(path_text: str | None, base: Path = PROJECT_ROOT) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute():
        return path
    return base / path


VALID_VERDICTS = {"issue_found", "no_issue_found"}
L1_RESPONSE_FIELDS = {"verdict", "selector", "target", "issue_type", "observed_behavior", "evidence"}
MULTI_RESPONSE_FIELDS = {"verdict", "issues"}
ISSUE_FIELDS = {"selector", "target", "issue_type", "observed_behavior", "evidence"}


def _rule_task_level(rule: dict[str, Any] | None) -> str | None:
    if not rule:
        return None
    level = rule.get("task_level")
    return str(level) if level is not None else None


def _reject_unsupported_fields(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unsupported = sorted(set(value) - allowed)
    if unsupported:
        raise ValueError(f"Links response {label} contains unsupported fields: {', '.join(unsupported)}.")


def normalize_issues(response: dict[str, Any], rule: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return reported issues under the current Links output contract."""

    task_level = _rule_task_level(rule)
    if task_level in {"level2", "level3"} or "issues" in response:
        _reject_unsupported_fields(response, MULTI_RESPONSE_FIELDS, "top level")
    else:
        _reject_unsupported_fields(response, L1_RESPONSE_FIELDS, "top level")

    verdict = response.get("verdict")
    if verdict not in VALID_VERDICTS:
        raise ValueError("Links response verdict must be `issue_found` or `no_issue_found`.")

    if task_level in {"level2", "level3"} and "issues" not in response:
        raise ValueError("L2/L3 Links responses must include an `issues` list.")
    if task_level == "level1" and "issues" in response:
        raise ValueError("L1 Links responses must use the single-issue output shape, not `issues`.")

    issues = response.get("issues")
    if issues is not None and not isinstance(issues, list):
        raise ValueError("Links response `issues` must be a list.")
    if isinstance(issues, list) and not all(isinstance(issue, dict) for issue in issues):
        raise ValueError("Links response `issues` entries must be objects.")
    if isinstance(issues, list):
        for index, issue in enumerate(issues):
            _reject_unsupported_fields(issue, ISSUE_FIELDS, f"issues[{index}]")

    if verdict == "no_issue_found":
        if isinstance(issues, list) and issues:
            raise ValueError("`no_issue_found` responses must not contain reported issues.")
        return []

    if isinstance(issues, list):
        if task_level in {"level2", "level3"} and not issues:
            raise ValueError("`issue_found` L2/L3 responses must include at least one issue.")
        return issues

    if any(key in response for key in ("selector", "target", "issue_type", "evidence")):
        return [response]
    return []


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def gold_selectors(rule: dict[str, Any]) -> list[str]:
    issues = gold_issues(rule)
    if issues:
        selectors: list[str] = []
        for issue in issues:
            selectors.extend(selectors_for_gold_issue(issue))
        return selectors

    target = ((rule.get("gold") or {}).get("target") or {})
    selectors: list[str] = []
    selectors.extend(_as_list(target.get("selector")))
    selectors.extend(_as_list(target.get("selectors")))
    return [selector.strip() for selector in selectors if selector and selector.strip()]


def gold_selector_groups(rule: dict[str, Any]) -> list[list[str]]:
    issues = gold_issues(rule)
    if issues:
        return [selectors_for_gold_issue(issue) for issue in issues]
    selectors = gold_selectors(rule)
    return [selectors] if selectors else []


def gold_issues(rule: dict[str, Any]) -> list[dict[str, Any]]:
    issues = (rule.get('gold') or {}).get('issues')
    if not isinstance(issues, list):
        return []
    return [issue for issue in issues if isinstance(issue, dict)]


def selectors_for_gold_issue(issue: dict[str, Any]) -> list[str]:
    target = issue.get('target') if isinstance(issue.get('target'), dict) else {}
    selectors: list[str] = []
    selectors.extend(_as_list(target.get('selector')))
    selectors.extend(_as_list(target.get('selectors')))
    return [selector.strip() for selector in selectors if selector and selector.strip()]


def compare_selector_sets(gold: list[str], agent: list[str]) -> dict[str, Any]:
    """Check whether agent-resolved element IDs are within the gold element set.

    The accepted relation is: agent set equals gold set, or agent set is a
    non-empty subset of gold. Any agent-resolved element outside gold is a fail.
    """

    gold_set = set(gold)
    agent_set = set(agent)
    extra_agent = sorted(agent_set - gold_set)
    missing_gold = sorted(gold_set - agent_set)
    exact_match = bool(gold_set) and agent_set == gold_set
    agent_subset = bool(gold_set) and bool(agent_set) and agent_set.issubset(gold_set)

    return {
        "match": exact_match or agent_subset,
        "relation": "exact" if exact_match else "agent_subset" if agent_subset else "mismatch",
        "gold_count": len(gold_set),
        "agent_count": len(agent_set),
        "missing_gold": missing_gold,
        "extra_agent": extra_agent,
    }


def _norm_text(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9.]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+\.\d+\.\d+\b", text))


def _criterion(rule: dict[str, Any]) -> dict[str, Any]:
    return ((rule.get("gold") or {}).get("criterion") or {})


def rule_for_gold_issue(rule: dict[str, Any], issue: dict[str, Any]) -> dict[str, Any]:
    return {'gold': {'criterion': issue.get('criterion') or {}}}


def issue_type_matches(agent_issue_type: str | dict[str, Any] | None, rule: dict[str, Any]) -> dict[str, Any]:
    """Match the single agent-facing issue_type field against the gold family."""

    criterion = _criterion(rule)
    expected_family = str(criterion.get("issue_family") or "").strip()

    if isinstance(agent_issue_type, dict):
        agent_raw = str(agent_issue_type.get("issue_type") or "")
    else:
        agent_raw = str(agent_issue_type or "")

    observed_family = agent_raw.strip()
    if expected_family and observed_family == expected_family:
        return {"match": True, "method": "issue_family", "expected": expected_family}

    return {
        "match": False,
        "method": "none",
        "expected": {"issue_family": expected_family},
        "observed": agent_raw,
    }


def issue_fields_for_issue(issue: dict[str, Any]) -> dict[str, Any] | str:
    return str(issue.get("issue_type") or "")


def _union_selector_ids(selector_map: dict[str, list[str]], selectors: list[str]) -> list[str]:
    ids: set[str] = set()
    for selector in selectors:
        ids.update(selector_map.get(selector, []))
    return sorted(ids)


def _gold_issue_family(issue: dict[str, Any]) -> str:
    criterion = issue.get('criterion') if isinstance(issue.get('criterion'), dict) else {}
    return str(criterion.get('issue_family') or '').strip()


def _agent_issue_family(issue: dict[str, Any]) -> str:
    issue_type = issue.get('issue_type')
    if isinstance(issue_type, dict):
        issue_type = issue_type.get('issue_type') or issue_type.get('issue_family')
    return str(issue_type or '').strip()


def build_element_expanded_result(
    issues: list[dict[str, Any]],
    expected: list[dict[str, Any]],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    gold_map = selector_resolutions.get('gold', {})
    agent_map = selector_resolutions.get('agent', {})

    expected_units: set[tuple[str, str]] = set()
    gold_units_by_index: list[set[tuple[str, str]]] = []
    per_gold: list[dict[str, Any]] = []

    for gold_index, gold_issue in enumerate(expected):
        issue_family = _gold_issue_family(gold_issue)
        selectors = selectors_for_gold_issue(gold_issue)
        element_ids = _union_selector_ids(gold_map, selectors)
        units = {(issue_family, element_id) for element_id in element_ids}
        gold_units_by_index.append(units)
        expected_units.update(units)
        per_gold.append(
            {
                'gold_index': gold_index,
                'issue_id': str(gold_issue.get('issue_id') or gold_index),
                'issue_family': issue_family,
                'expected_element_count': len(units),
                'matched_element_count': 0,
                'missing_element_count': len(units),
                'matched_agent_issue_indices': [],
            }
        )

    reported_units: set[tuple[str, str]] = set()
    unresolved_units: set[tuple[str, str]] = set()
    unit_sources: dict[tuple[str, str], set[int]] = {}
    duplicate_reported_elements = 0
    raw_resolved_reported_elements = 0
    unresolved_reported_issues = 0

    for agent_index, issue in enumerate(issues):
        issue_family = _agent_issue_family(issue)
        selector = str(issue.get('selector') or '').strip()
        element_ids = sorted(set(agent_map.get(selector, [])))

        if not element_ids:
            unresolved_reported_issues += 1
            unit = (issue_family, f'__unresolved_issue_{agent_index}__')
            reported_units.add(unit)
            unresolved_units.add(unit)
            unit_sources.setdefault(unit, set()).add(agent_index)
            continue

        raw_resolved_reported_elements += len(element_ids)
        for element_id in element_ids:
            unit = (issue_family, element_id)
            if unit in reported_units:
                duplicate_reported_elements += 1
            reported_units.add(unit)
            unit_sources.setdefault(unit, set()).add(agent_index)

    matched_units = reported_units & expected_units
    extra_units = reported_units - expected_units

    for gold_index, units in enumerate(gold_units_by_index):
        matched_for_gold = units & matched_units
        agent_indices: set[int] = set()
        for unit in matched_for_gold:
            agent_indices.update(unit_sources.get(unit, set()))
        per_gold[gold_index]['matched_element_count'] = len(matched_for_gold)
        per_gold[gold_index]['missing_element_count'] = len(units - matched_for_gold)
        per_gold[gold_index]['matched_agent_issue_indices'] = sorted(agent_indices)

    expected_count = len(expected_units)
    reported_distinct_count = len(reported_units)
    reported_raw_count = raw_resolved_reported_elements + unresolved_reported_issues
    matched_count = len(matched_units)
    recall = matched_count / expected_count if expected_count else 1.0
    precision = matched_count / reported_distinct_count if reported_distinct_count else 0.0

    return {
        'expected_elements': expected_count,
        'reported_elements': reported_distinct_count,
        'reported_elements_distinct': reported_distinct_count,
        'reported_elements_raw': reported_raw_count,
        'raw_resolved_reported_elements': raw_resolved_reported_elements,
        'matched_elements': matched_count,
        'extra_elements': len(extra_units),
        'resolved_extra_elements': len(extra_units - unresolved_units),
        'duplicate_reported_elements': duplicate_reported_elements,
        'unresolved_reported_issues': unresolved_reported_issues,
        'unresolved_reported_units': len(unresolved_units),
        'recall': recall,
        'precision': precision,
        'per_gold_issue': per_gold,
    }


def _issue_present(rule: dict[str, Any]) -> bool:
    gold = rule.get('gold') or {}
    expected_verdict = str(gold.get('expected_verdict') or '').strip()
    return bool(gold.get('issue_present', expected_verdict == 'issue_found'))


def gold_resolution_errors(rule: dict[str, Any], selector_resolutions: dict[str, dict[str, list[str]]]) -> list[dict[str, Any]]:
    if not _issue_present(rule):
        return []

    gold_map = selector_resolutions.get('gold', {})
    errors: list[dict[str, Any]] = []
    issues = gold_issues(rule)
    if issues:
        for gold_index, issue in enumerate(issues):
            selectors = selectors_for_gold_issue(issue)
            gold_ids = _union_selector_ids(gold_map, selectors)
            if not selectors or not gold_ids:
                errors.append(
                    {
                        'gold_index': gold_index,
                        'issue_id': str(issue.get('issue_id') or gold_index),
                        'selectors': selectors,
                        'reason': 'missing_gold_selector' if not selectors else 'no_gold_elements',
                    }
                )
        return errors

    selectors = gold_selectors(rule)
    gold_ids = _union_selector_ids(gold_map, selectors)
    if not selectors or not gold_ids:
        errors.append(
            {
                'selectors': selectors,
                'reason': 'missing_gold_selector' if not selectors else 'no_gold_elements',
            }
        )
    return errors


def _with_evaluator_status(
    result: dict[str, Any],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    errors = gold_resolution_errors(rule, selector_resolutions)
    result['evaluator_error'] = bool(errors)
    result['error_type'] = 'gold_resolution' if errors else None
    result['gold_resolution_errors'] = errors
    if errors:
        result['overall_pass'] = False
    return result


def evaluate_multi_gold_response(
    response: dict[str, Any],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    gold = rule.get('gold') or {}
    expected_verdict = str(gold.get('expected_verdict') or '').strip()
    observed_verdict = str(response.get('verdict') or '').strip()
    verdict_match = bool(expected_verdict) and observed_verdict == expected_verdict
    expected = gold_issues(rule)
    issues = normalize_issues(response, rule)
    unmatched_agent_indices = set(range(len(issues)))
    matched_indices: list[int] = []
    gold_results: list[dict[str, Any]] = []

    for gold_index, gold_issue in enumerate(expected):
        selectors = selectors_for_gold_issue(gold_issue)
        gold_ids = _union_selector_ids(selector_resolutions.get('gold', {}), selectors)
        candidate_results: list[dict[str, Any]] = []
        matched_index: int | None = None
        matched_result: dict[str, Any] | None = None

        for agent_index, issue in enumerate(issues):
            if agent_index not in unmatched_agent_indices:
                continue
            selector = str(issue.get('selector') or '').strip()
            agent_ids = selector_resolutions.get('agent', {}).get(selector, [])
            selector_result = compare_selector_sets(gold_ids, agent_ids)
            issue_result = issue_type_matches(issue_fields_for_issue(issue), rule_for_gold_issue(rule, gold_issue))
            issue_pass = selector_result['match'] and issue_result['match']
            candidate = {
                'index': agent_index,
                'selector': selector,
                'selector_match': selector_result['match'],
                'selector_relation': selector_result['relation'],
                'selector_result': selector_result,
                'issue_type_match': issue_result['match'],
                'issue_type_result': issue_result,
                'issue_pass': issue_pass,
            }
            candidate_results.append(candidate)
            if issue_pass and matched_index is None:
                matched_index = agent_index
                matched_result = candidate

        if matched_index is not None:
            unmatched_agent_indices.remove(matched_index)
            matched_indices.append(matched_index)

        gold_results.append(
            {
                'gold_index': gold_index,
                'issue_id': str(gold_issue.get('issue_id') or gold_index),
                'gold_selectors': selectors,
                'gold_element_ids': gold_ids,
                'matched_issue_index': matched_index,
                'selector_match': matched_result['selector_match'] if matched_result else False,
                'issue_type_match': matched_result['issue_type_match'] if matched_result else False,
                'match': matched_index is not None,
                'matched_result': matched_result,
                'candidate_results': candidate_results,
            }
        )

    duplicate_matched_indices: set[int] = set()
    matched_index_set = set(matched_indices)
    for gold_result in gold_results:
        matched_index = gold_result.get('matched_issue_index')
        if matched_index is None:
            continue
        for candidate in gold_result.get('candidate_results') or []:
            candidate_index = candidate.get('index')
            if (
                candidate.get('issue_pass')
                and candidate_index != matched_index
                and candidate_index not in matched_index_set
            ):
                duplicate_matched_indices.add(candidate_index)

    expected_count = len(expected)
    raw_reported_count = len(issues)
    matched_count = len(matched_indices)
    extra_issues = sorted(unmatched_agent_indices - duplicate_matched_indices)
    reported_count = matched_count + len(extra_issues)
    missing_gold = [item['issue_id'] for item in gold_results if not item['match']]
    recall = matched_count / expected_count if expected_count else 1.0
    precision = matched_count / reported_count if reported_count else 0.0
    element_expanded = build_element_expanded_result(issues, expected, selector_resolutions)
    issue_present = bool(gold.get('issue_present', expected_verdict == 'issue_found'))

    if issue_present:
        selector_match = matched_count == expected_count
        issue_type_match = matched_count == expected_count
        overall_pass = verdict_match and matched_count == expected_count and not extra_issues
    else:
        selector_match = True
        issue_type_match = True
        overall_pass = verdict_match and reported_count == 0

    return {
        'overall_pass': overall_pass,
        'verdict_match': verdict_match,
        'expected_verdict': expected_verdict,
        'observed_verdict': observed_verdict,
        'selector_match': selector_match,
        'issue_type_match': issue_type_match,
        'matched_issue_indices': sorted(matched_indices),
        'matched_issue_index': sorted(matched_indices)[0] if matched_indices else None,
        'expected_count': expected_count,
        'reported_count': reported_count,
        'raw_reported_count': raw_reported_count,
        'matched_count': matched_count,
        'missing_gold': missing_gold,
        'extra_issues': extra_issues,
        'duplicate_matched_issue_indices': sorted(duplicate_matched_indices),
        'recall': recall,
        'precision': precision,
        'element_expanded': element_expanded,
        'gold_selectors': gold_selectors(rule),
        'gold_issue_results': gold_results,
        'issue_count': reported_count,
        'issue_results': gold_results,
        'extra_issue_indices': extra_issues,
    }


def evaluate_response_against_rule(
    response: dict[str, Any],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    if gold_issues(rule):
        return _with_evaluator_status(
            evaluate_multi_gold_response(response, rule, selector_resolutions),
            rule,
            selector_resolutions,
        )

    gold = rule.get("gold") or {}
    expected_verdict = str(gold.get("expected_verdict") or "").strip()
    observed_verdict = str(response.get("verdict") or "").strip()
    verdict_match = bool(expected_verdict) and observed_verdict == expected_verdict
    selectors = gold_selectors(rule)
    gold_ids = _union_selector_ids(selector_resolutions.get("gold", {}), selectors)
    issues = normalize_issues(response, rule)

    issue_results: list[dict[str, Any]] = []
    matched_index: int | None = None

    for index, issue in enumerate(issues):
        selector = str(issue.get("selector") or "").strip()
        agent_ids = selector_resolutions.get("agent", {}).get(selector, [])
        selector_result = compare_selector_sets(gold_ids, agent_ids)
        issue_result = issue_type_matches(issue_fields_for_issue(issue), rule)
        issue_pass = selector_result["match"] and issue_result["match"]
        if issue_pass and matched_index is None:
            matched_index = index
        issue_results.append(
            {
                "index": index,
                "selector": selector,
                "selector_match": selector_result["match"],
                "selector_relation": selector_result["relation"],
                "selector_result": selector_result,
                "issue_type_match": issue_result["match"],
                "issue_type_result": issue_result,
                "issue_pass": issue_pass,
            }
        )

    issue_present = bool(gold.get("issue_present", expected_verdict == "issue_found"))
    if issue_present:
        selector_match = matched_index is not None
        issue_type_match = matched_index is not None
        overall_pass = verdict_match and matched_index is not None
    else:
        selector_match = True
        issue_type_match = True
        overall_pass = verdict_match

    result = {
        "overall_pass": overall_pass,
        "verdict_match": verdict_match,
        "expected_verdict": expected_verdict,
        "observed_verdict": observed_verdict,
        "selector_match": selector_match,
        "issue_type_match": issue_type_match,
        "matched_issue_index": matched_index,
        "gold_selectors": selectors,
        "gold_element_ids": gold_ids,
        "issue_count": len(issues),
        "issue_results": issue_results,
        "extra_issue_indices": [
            result["index"] for result in issue_results if result["index"] != matched_index
        ],
    }
    return _with_evaluator_status(result, rule, selector_resolutions)


async def _resolve_selector_once(page: Any, selector: str) -> tuple[list[str], str | None]:
    if not selector:
        return [], "empty selector"
    try:
        ids = await page.eval_on_selector_all(
            selector,
            """
            elements => elements.map(element => {
                if (!element.__gtLinksEvalId) {
                    const nextId = (window.__gtLinksEvalSeq = (window.__gtLinksEvalSeq || 0) + 1);
                    Object.defineProperty(element, '__gtLinksEvalId', {
                        value: `gt-links-eval-${nextId}`,
                        configurable: true,
                    });
                }
                return element.__gtLinksEvalId;
            })
            """,
        )
    except Exception as exc:  # Playwright raises on invalid selectors.
        return [], str(exc)
    return [str(item) for item in ids], None


async def _resolve_one_selector(
    page: Any,
    selector: str,
    *,
    timeout_ms: int = 2_000,
    poll_ms: int = 100,
    stable_ms: int = 500,
) -> tuple[list[str], str | None]:
    deadline = time.perf_counter() + max(timeout_ms, 0) / 1000
    stable_since: float | None = None
    last_ids: list[str] = []
    last_error: str | None = None

    while True:
        ids, error = await _resolve_selector_once(page, selector)
        if error:
            return [], error

        now = time.perf_counter()
        if ids:
            if ids == last_ids:
                if stable_since is None:
                    stable_since = now
                if (now - stable_since) * 1000 >= stable_ms:
                    return ids, None
            else:
                stable_since = now
            last_ids = ids
        else:
            stable_since = None
            last_ids = []
            last_error = error

        if now >= deadline:
            return last_ids, last_error
        await page.wait_for_timeout(min(poll_ms, max(1, int((deadline - now) * 1000))))


async def _wait_for_gold_selector_groups(page: Any, selector_groups: list[list[str]], timeout_ms: int) -> None:
    groups = [[selector for selector in group if selector] for group in selector_groups]
    groups = [group for group in groups if group]
    if not groups:
        return
    try:
        await page.wait_for_function(
            """
            groups => groups.every(group => group.some(selector => {
                try {
                    return document.querySelector(selector) !== null;
                } catch {
                    return true;
                }
            }))
            """,
            groups,
            timeout=timeout_ms,
        )
    except Exception:
        # Missing gold selectors are reported explicitly after resolution.
        return


async def resolve_selectors_on_page(
    start_url: str,
    gold_selector_list: list[str],
    gold_selector_group_list: list[list[str]],
    agent_selector_list: list[str],
    storage_state_path: Path | None,
    headless: bool,
    timeout_ms: int,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            context_kwargs: dict[str, Any] = {"viewport": {"width": 1280, "height": 900}}
            if storage_state_path is not None:
                context_kwargs["storage_state"] = str(storage_state_path)
            context = await browser.new_context(**context_kwargs)
            page = await context.new_page()
            response = await page.goto(start_url, wait_until="domcontentloaded", timeout=timeout_ms)
            try:
                await page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 8000))
            except Exception:
                pass
            await _wait_for_gold_selector_groups(page, gold_selector_group_list, timeout_ms=min(timeout_ms, 8000))
            await page.evaluate("window.__gtLinksEvalSeq = 0")

            resolved: dict[str, dict[str, list[str]]] = {"gold": {}, "agent": {}}
            errors: list[dict[str, str]] = []
            for selector in gold_selector_list:
                ids, error = await _resolve_one_selector(page, selector)
                resolved["gold"][selector] = ids
                if error:
                    errors.append({"side": "gold", "selector": selector, "error": error})
            for selector in agent_selector_list:
                ids, error = await _resolve_one_selector(page, selector)
                resolved["agent"][selector] = ids
                if error:
                    errors.append({"side": "agent", "selector": selector, "error": error})

            return {
                "start_url": start_url,
                "final_url": page.url,
                "http_status": response.status if response is not None else None,
                "selector_resolutions": resolved,
                "selector_errors": errors,
            }
        finally:
            await browser.close()


def start_url_from_snapshots(task: dict[str, Any], rule: dict[str, Any]) -> str:
    page = rule.get("page") if isinstance(rule.get("page"), dict) else {}
    start_url = page.get("start_url") or task.get("start_url")
    if not start_url:
        raise ValueError("No start_url found in task or evaluate-rule snapshot")
    return str(start_url)


def storage_state_from_run(run_dir: Path, task: dict[str, Any], meta: dict[str, Any], override: str | None) -> Path | None:
    candidates = [
        resolve_path(override),
        resolve_path(meta.get("auth_state_file")),
        resolve_path(task.get("auth_state_file")),
    ]
    for candidate in candidates:
        if candidate is not None and candidate.exists():
            return candidate
    local_candidates = sorted(run_dir.glob("*.storage_state.json")) + sorted(run_dir.glob("storage_state_*.json"))
    for candidate in local_candidates:
        if candidate.exists():
            return candidate
    return None


def _auth_required(task: dict[str, Any], meta: dict[str, Any], override: str | None) -> bool:
    return bool(task.get("auth_state_file") or meta.get("auth_state_file") or override)


def infer_eval_site(task: dict[str, Any], rule: dict[str, Any], meta: dict[str, Any]) -> str | None:
    page = rule.get("page") if isinstance(rule.get("page"), dict) else {}
    for source, key in ((page, "site"), (task, "site"), (meta, "site"), (meta, "auth_refresh_site")):
        value = source.get(key) if isinstance(source, dict) else None
        if value:
            return str(value)
    for source in (task, rule, meta):
        if not isinstance(source, dict):
            continue
        for key in ("instance_id", "task_id"):
            value = str(source.get(key) or "")
            if "." in value:
                return value.split(".", 1)[0]
    return None


async def refresh_eval_auth_state(site: str, output_path: Path, headless: bool = True) -> Path:
    from agent.gt.save_storage_state import create_storage_state

    safe_mkdir(output_path.parent)
    await create_storage_state(site, output_path, headed=not headless)
    return output_path


async def probe_eval_auth_state(site: str, storage_state_path: Path) -> tuple[bool, str]:
    from agent.gt.probe_auth import probe

    return await probe(site, storage_state_path)


def _auth_status(mode: str, site: str | None, storage_state_path: Path | None, probe_ok: bool | None, probe_reason: str | None) -> dict[str, Any]:
    return {
        "mode": mode,
        "site": site,
        "storage_state_file": str(storage_state_path) if storage_state_path else None,
        "probe_ok": probe_ok,
        "probe_reason": probe_reason,
    }


def _auth_error_result(
    run_dir: Path,
    task: dict[str, Any],
    rule: dict[str, Any],
    start_url: str,
    storage_state_path: Path | None,
    auth: dict[str, Any],
    error_type: str,
) -> dict[str, Any]:
    return {
        "run_dir": str(run_dir),
        "task_id": task.get("task_id"),
        "instance_id": task.get("instance_id"),
        "task_level": rule.get("task_level"),
        "storage_state_file": str(storage_state_path) if storage_state_path else None,
        "auth": auth,
        "page": {"start_url": start_url, "final_url": None, "http_status": None},
        "selector_errors": [],
        "overall_pass": False,
        "evaluator_error": True,
        "error_type": error_type,
        "gold_resolution_errors": [],
    }


def _response_format_error_result(run_dir: Path, task: dict[str, Any], rule: dict[str, Any], start_url: str, response: dict[str, Any], error: Exception) -> dict[str, Any]:
    gold = rule.get("gold") if isinstance(rule.get("gold"), dict) else {}
    return {
        "run_dir": str(run_dir),
        "task_id": task.get("task_id"),
        "instance_id": task.get("instance_id"),
        "task_level": rule.get("task_level"),
        "storage_state_file": None,
        "auth": _auth_status("not_needed_for_response_format_error", None, None, None, None),
        "page": {"start_url": start_url, "final_url": None, "http_status": None, "precondition_actions": []},
        "selector_errors": [],
        "overall_pass": False,
        "verdict_match": False,
        "expected_verdict": str(gold.get("expected_verdict") or "").strip(),
        "observed_verdict": str(response.get("verdict") or "").strip() if isinstance(response, dict) else "",
        "normalization_warnings": [],
        "selector_match": False,
        "issue_type_match": False,
        "reported_count": 0,
        "raw_reported_count": 0,
        "matched_count": 0,
        "evaluator_error": False,
        "error_type": "response_format_error",
        "response_format_error": str(error),
        "gold_resolution_errors": [],
    }


async def storage_state_for_evaluation(
    run_dir: Path,
    task: dict[str, Any],
    rule: dict[str, Any],
    meta: dict[str, Any],
    override: str | None,
    headless: bool,
) -> tuple[Path | None, dict[str, Any]]:
    if not _auth_required(task, meta, override):
        return None, _auth_status("none", None, None, None, None)

    site = infer_eval_site(task, rule, meta)
    if not site:
        raise ValueError(f"Cannot infer site for eval auth refresh: {task.get('task_id') or run_dir}")

    if override:
        storage_state_path = resolve_path(override)
        if storage_state_path is None or not storage_state_path.exists():
            raise FileNotFoundError(f"Auth state file not found: {override}")
        mode = "override"
    else:
        storage_state_path = eval_auth_state_path_for_run(run_dir, site)
        mode = "fresh"
        try:
            storage_state_path = await refresh_eval_auth_state(site, storage_state_path, headless=headless)
        except Exception as exc:
            return storage_state_path, _auth_status(mode, site, storage_state_path, False, str(exc))

    try:
        probe_ok, probe_reason = await probe_eval_auth_state(site, storage_state_path)
    except Exception as exc:
        probe_ok, probe_reason = False, str(exc)
    return storage_state_path, _auth_status(mode, site, storage_state_path, probe_ok, probe_reason)


async def evaluate_run_dir(
    run_dir: Path,
    *,
    auth_state_file: str | None = None,
    headless: bool = True,
    timeout_ms: int = 30000,
) -> dict[str, Any]:
    task_path = run_dir / "task.snapshot.yaml"
    rule_path = run_dir / "evaluate-rule.snapshot.yaml"
    response_path = run_dir / "final-response.json"
    meta_path = run_dir / "meta.json"

    for required in (task_path, rule_path, response_path):
        if not required.exists():
            raise FileNotFoundError(f"Required run artifact not found: {required}")

    task = load_yaml(task_path)
    rule = load_yaml(rule_path)
    response = load_json(response_path)
    meta = load_json(meta_path) if meta_path.exists() else {}
    start_url = start_url_from_snapshots(task, rule)

    try:
        issues = normalize_issues(response, rule)
    except ValueError as exc:
        return _response_format_error_result(run_dir, task, rule, start_url, response, exc)

    storage_state_path, auth = await storage_state_for_evaluation(run_dir, task, rule, meta, auth_state_file, headless)
    if auth.get("probe_ok") is False:
        return _auth_error_result(run_dir, task, rule, start_url, storage_state_path, auth, "auth_probe")

    agent_selectors = [str(issue.get("selector") or "").strip() for issue in issues]
    agent_selectors = [selector for selector in agent_selectors if selector]
    gold_selector_list = gold_selectors(rule)
    gold_selector_group_list = gold_selector_groups(rule)

    page_result = await resolve_selectors_on_page(
        start_url=start_url,
        gold_selector_list=gold_selector_list,
        gold_selector_group_list=gold_selector_group_list,
        agent_selector_list=agent_selectors,
        storage_state_path=storage_state_path,
        headless=headless,
        timeout_ms=timeout_ms,
    )
    rule_result = evaluate_response_against_rule(
        response,
        rule,
        page_result["selector_resolutions"],
    )

    return {
        "run_dir": str(run_dir),
        "task_id": task.get("task_id"),
        "instance_id": task.get("instance_id"),
        "task_level": rule.get("task_level"),
        "storage_state_file": str(storage_state_path) if storage_state_path else None,
        "auth": auth,
        "page": {
            "start_url": page_result["start_url"],
            "final_url": page_result["final_url"],
            "http_status": page_result["http_status"],
        },
        "selector_errors": page_result["selector_errors"],
        **rule_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate one completed Links GT run directory.")
    parser.add_argument("--run-dir", required=True, type=Path, help="Directory containing task/evaluate/response artifacts.")
    parser.add_argument("--auth-state-file", help="Optional Playwright storage-state override.")
    parser.add_argument("--output", type=Path, help="Optional path for evaluation JSON.")
    parser.add_argument("--headed", action="store_true", help="Show the Playwright browser while evaluating.")
    parser.add_argument("--timeout", type=int, default=30000, help="Navigation timeout in milliseconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = asyncio.run(
            evaluate_run_dir(
                args.run_dir,
                auth_state_file=args.auth_state_file,
                headless=not args.headed,
                timeout_ms=args.timeout,
            )
        )
    except Exception as exc:
        print(f"evaluate_run failed: {exc}", file=sys.stderr)
        sys.exit(2)

    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if result.get("evaluator_error"):
        sys.exit(2)
    sys.exit(0 if result.get("overall_pass") else 1)


if __name__ == "__main__":
    main()

