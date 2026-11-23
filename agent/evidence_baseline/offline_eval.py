from __future__ import annotations

import re
from typing import Any


def _norm(value: Any) -> str:
    return str(value or '').strip().lower()


def _norm_words(value: Any) -> list[str]:
    return [word for word in re.sub(r'[^a-z0-9]+', ' ', _norm(value)).split() if word]


def _candidate_text(candidate: dict[str, Any]) -> str:
    fields = ('id', 'label', 'text', 'ariaLabel', 'title', 'role', 'selector')
    return ' '.join(_norm(candidate.get(field)).replace('_', ' ') for field in fields)


def _target_aliases(rule: dict[str, Any]) -> list[str]:
    gold = rule.get('gold') or {}
    aliases = gold.get('target_aliases') or []
    if isinstance(aliases, str):
        return [aliases]
    return [str(alias) for alias in aliases if str(alias).strip()]


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def _split_selector_list(selector: str) -> list[str]:
    return [part.strip() for part in str(selector or '').split(',') if part.strip()]


def _target_selectors(target: dict[str, Any]) -> list[str]:
    selectors: list[str] = []
    selectors.extend(_as_list(target.get('selector')))
    selectors.extend(_as_list(target.get('selectors')))
    expanded: list[str] = []
    for selector in selectors:
        expanded.extend(_split_selector_list(selector))
    return [selector.strip() for selector in expanded if selector.strip()]


def _gold_issues(rule: dict[str, Any]) -> list[dict[str, Any]]:
    issues = (rule.get('gold') or {}).get('issues')
    if not isinstance(issues, list):
        return []
    return [issue for issue in issues if isinstance(issue, dict)]


def _selectors_for_gold_issue(issue: dict[str, Any]) -> list[str]:
    target = issue.get('target') if isinstance(issue.get('target'), dict) else {}
    return _target_selectors(target)


def _gold_selectors(rule: dict[str, Any]) -> list[str]:
    issues = _gold_issues(rule)
    if issues:
        selectors: list[str] = []
        for issue in issues:
            selectors.extend(_selectors_for_gold_issue(issue))
        return selectors
    target = ((rule.get('gold') or {}).get('target') or {})
    return _target_selectors(target)


def _gold_selector_groups(rule: dict[str, Any]) -> list[list[str]]:
    issues = _gold_issues(rule)
    if issues:
        return [selectors for issue in issues if (selectors := _selectors_for_gold_issue(issue))]
    selectors = _gold_selectors(rule)
    return [selectors] if selectors else []


def _is_confirmed_issue(rule: dict[str, Any]) -> bool:
    gold = rule.get('gold') or {}
    verdict = gold.get('verdict') or {}
    status = _norm(verdict.get('status'))
    if status == 'pass':
        return False
    if gold.get('issue_present') is False:
        return False
    if _norm(gold.get('expected_verdict')) == 'no_issue_found':
        return False
    return True


def _alias_matches_candidate(alias: str, candidate: dict[str, Any]) -> bool:
    candidate_words = set(word for word in _norm_words(_candidate_text(candidate)) if len(word) >= 3)
    words = [word for word in _norm_words(alias) if len(word) >= 3]
    if not words:
        return False
    if all(word in candidate_words for word in words):
        return True
    if len(words) >= 2 and any(words[index] in candidate_words and words[index + 1] in candidate_words for index in range(len(words) - 1)):
        return True
    return False


def _base_result(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'candidate_count': len(candidates),
        'gold_target_count': 0,
        'matched_target_count': 0,
        'matched_candidate_count': 0,
        'precision': None,
        'recall': None,
        'match_basis': None,
        'false_positive_count': 0,
        'false_positive_rate': 0.0,
    }


def _manifest_candidates(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return list(manifest.get('suspect_candidates') or [])


def _confirmed_result(
    candidates: list[dict[str, Any]],
    *,
    gold_target_count: int,
    matched_target_count: int,
    matched_candidate_count: int,
    match_basis: str | None,
) -> dict[str, Any]:
    result = _base_result(candidates)
    result.update({
        'gold_target_count': gold_target_count,
        'matched_target_count': matched_target_count,
        'matched_candidate_count': matched_candidate_count,
        'precision': matched_candidate_count / len(candidates) if candidates else 0.0,
        'recall': matched_target_count / gold_target_count if gold_target_count else None,
        'match_basis': match_basis,
    })
    return result


def _resolution_side(selector_resolutions: dict[str, dict[str, list[str]]], side: str) -> dict[str, list[str]]:
    if side == 'candidate':
        return selector_resolutions.get('candidate') or selector_resolutions.get('agent') or {}
    return selector_resolutions.get(side) or {}


def _union_selector_ids(resolved: dict[str, list[str]], selectors: list[str]) -> set[str]:
    ids: set[str] = set()
    for selector in selectors:
        ids.update(str(item) for item in resolved.get(selector, []) if str(item).strip())
    return ids


def _candidate_resolved_ids(candidate: dict[str, Any], selector_resolutions: dict[str, dict[str, list[str]]]) -> set[str]:
    selector = str(candidate.get('selector') or '').strip()
    if not selector:
        return set()
    return set(_resolution_side(selector_resolutions, 'candidate').get(selector, []))


def _candidate_matches_gold_ids(candidate_ids: set[str], gold_ids: set[str]) -> bool:
    return bool(candidate_ids & gold_ids) and len(candidate_ids) <= max(len(gold_ids), 1)


def _candidate_selector(candidate: dict[str, Any]) -> str:
    return str(candidate.get('selector') or '').strip()


def _candidate_matches_gold_relation(candidate: dict[str, Any], gold_selectors: list[str], selector_resolutions: dict[str, Any]) -> bool:
    return bool(_candidate_gold_relation_ids(candidate, gold_selectors, selector_resolutions))


def _candidate_gold_relation_ids(candidate: dict[str, Any], gold_selectors: list[str], selector_resolutions: dict[str, Any]) -> set[str]:
    selector = _candidate_selector(candidate)
    if not selector:
        return set()
    agent_to_gold = ((selector_resolutions.get('relations') or {}).get('agent_to_gold') or {})
    relations_by_gold = agent_to_gold.get(selector) or {}
    gold_ids: set[str] = set()
    for gold_selector in gold_selectors:
        for relation in relations_by_gold.get(gold_selector, []) or []:
            if str(relation.get('relation') or '') in {'exact', 'candidate_descendant_of_gold'}:
                gold_id = str(relation.get('gold_id') or '').strip()
                if gold_id:
                    gold_ids.add(gold_id)
    return gold_ids


_ID_SELECTOR_RE = re.compile(r'#([A-Za-z0-9_-]+)')


def _norm_selector(selector: str) -> str:
    return ''.join(str(selector or '').strip().lower().split())


def _selector_ids(selector: str) -> set[str]:
    return {match.group(1).lower() for match in _ID_SELECTOR_RE.finditer(str(selector or ''))}


def _candidate_identity_ids(candidate: dict[str, Any]) -> set[str]:
    ids = _selector_ids(str(candidate.get('selector') or ''))
    candidate_id = str(candidate.get('id') or '').strip().lower()
    if candidate_id:
        ids.add(candidate_id)
    return ids


def _looks_like_magento_filter_datepicker(candidate: dict[str, Any]) -> bool:
    if str(candidate.get('tag') or '').upper() != 'BUTTON':
        return False
    selector = _norm_selector(str(candidate.get('selector') or ''))
    if 'ui-datepicker-trigger' in selector:
        return True
    return 'thead' in selector and 'td:nth-of-type' in selector and selector.endswith('>button')


def _candidate_matches_gold_selector_fallback(candidate: dict[str, Any], gold_selectors: list[str]) -> bool:
    candidate_selector = str(candidate.get('selector') or '')
    normalized_candidate_selector = _norm_selector(candidate_selector)
    if not normalized_candidate_selector:
        return False

    candidate_ids = _candidate_identity_ids(candidate)
    for gold_selector in gold_selectors:
        normalized_gold_selector = _norm_selector(gold_selector)
        if not normalized_gold_selector:
            continue
        if normalized_candidate_selector == normalized_gold_selector:
            return True

        gold_ids = _selector_ids(gold_selector)
        if candidate_ids and gold_ids and candidate_ids & gold_ids:
            return True

        if normalized_gold_selector == 'button.ui-datepicker-trigger' and _looks_like_magento_filter_datepicker(candidate):
            return True
    return False


def _evaluate_multi_gold_with_resolved_selectors(
    candidates: list[dict[str, Any]],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    issues = _gold_issues(rule)
    gold_resolutions = _resolution_side(selector_resolutions, 'gold')
    candidate_ids_by_index = [
        _candidate_resolved_ids(candidate, selector_resolutions)
        for candidate in candidates
    ]

    per_gold_issue: list[dict[str, Any]] = []
    matched_candidate_indices: set[int] = set()
    used_resolution_match = False
    used_fallback_match = False
    for index, issue in enumerate(issues):
        selectors = _selectors_for_gold_issue(issue)
        gold_ids = _union_selector_ids(gold_resolutions, selectors)
        matched_indices: list[int] = []
        matched_markers: list[str] = []
        matched_bases: list[str] = []
        for candidate_index, candidate_ids in enumerate(candidate_ids_by_index):
            resolution_match = _candidate_matches_gold_ids(candidate_ids, gold_ids)
            relation_match = False if resolution_match else _candidate_matches_gold_relation(candidates[candidate_index], selectors, selector_resolutions)
            fallback_match = False if resolution_match else _candidate_matches_gold_selector_fallback(candidates[candidate_index], selectors)
            if resolution_match or fallback_match:
                matched_indices.append(candidate_index)
                marker = candidates[candidate_index].get('marker_id')
                matched_markers.append(str(marker if marker is not None else candidate_index))
                matched_candidate_indices.add(candidate_index)
                if relation_match and 'selector_relation' not in matched_bases:
                    matched_bases.append('selector_relation')
                elif resolution_match and 'selector_resolution' not in matched_bases:
                    matched_bases.append('selector_resolution')
                if fallback_match and 'selector_fallback' not in matched_bases:
                    matched_bases.append('selector_fallback')
                used_resolution_match = used_resolution_match or resolution_match
                used_fallback_match = used_fallback_match or fallback_match
        per_gold_issue.append({
            'gold_index': index,
            'issue_id': str(issue.get('issue_id') or index),
            'gold_selectors': selectors,
            'gold_element_count': len(gold_ids),
            'matched': bool(matched_indices),
            'matched_candidate_indices': matched_indices,
            'matched_markers': matched_markers,
            'match_basis': matched_bases,
        })

    matched_target_count = sum(1 for item in per_gold_issue if item['matched'])
    result = _confirmed_result(
        candidates,
        gold_target_count=len(issues),
        matched_target_count=matched_target_count,
        matched_candidate_count=len(matched_candidate_indices),
        match_basis=(
            'multi_selector_resolution+selector_fallback'
            if used_resolution_match and used_fallback_match else
            'multi_selector_resolution'
            if used_resolution_match else
            'multi_selector_fallback'
            if used_fallback_match else
            None
        ),
    )
    result['gold_target_unit'] = 'issue'
    result['gold_issue_results'] = per_gold_issue
    return result


def _multi_gold_false_positive_count(
    candidates: list[dict[str, Any]],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> int:
    issues = _gold_issues(rule)
    gold_resolutions = _resolution_side(selector_resolutions, 'gold')
    gold_ids_by_issue = [
        _union_selector_ids(gold_resolutions, _selectors_for_gold_issue(issue))
        for issue in issues
    ]

    false_positive_count = 0
    for candidate in candidates:
        candidate_ids = _candidate_resolved_ids(candidate, selector_resolutions)
        issue_selectors = [_selectors_for_gold_issue(issue) for issue in issues]
        if any(_candidate_matches_gold_ids(candidate_ids, gold_ids) for gold_ids in gold_ids_by_issue):
            false_positive_count += 1
        elif any(_candidate_matches_gold_relation(candidate, selectors, selector_resolutions) for selectors in issue_selectors):
            false_positive_count += 1
        elif any(_candidate_matches_gold_selector_fallback(candidate, selectors) for selectors in issue_selectors):
            false_positive_count += 1
    return false_positive_count


def _pass_result(candidates: list[dict[str, Any]], false_positive_count: int) -> dict[str, Any]:
    result = _base_result(candidates)
    result['false_positive_count'] = false_positive_count
    result['false_positive_rate'] = 1.0 if false_positive_count > 0 else 0.0
    return result


def _evaluate_alias_matches(candidates: list[dict[str, Any]], aliases: list[str]) -> dict[str, Any]:
    matched_candidate_count = 0
    for candidate in candidates:
        candidate_matched = False
        for alias in aliases:
            if _alias_matches_candidate(alias, candidate):
                candidate_matched = True
        if candidate_matched:
            matched_candidate_count += 1
    gold_target_count = 1 if aliases else 0
    return _confirmed_result(
        candidates,
        gold_target_count=gold_target_count,
        matched_target_count=1 if matched_candidate_count and gold_target_count else 0,
        matched_candidate_count=matched_candidate_count,
        match_basis='alias_text' if matched_candidate_count else None,
    )


def evaluate_candidate_manifest(
    manifest: dict[str, Any],
    rule: dict[str, Any],
) -> dict[str, Any]:
    candidates = _manifest_candidates(manifest)
    if not _is_confirmed_issue(rule):
        return _pass_result(candidates, false_positive_count=len(candidates))
    return _evaluate_alias_matches(candidates, _target_aliases(rule))


def evaluate_candidate_manifest_with_resolved_selectors(
    manifest: dict[str, Any],
    rule: dict[str, Any],
    selector_resolutions: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    candidates = _manifest_candidates(manifest)
    if _gold_issues(rule):
        if not _is_confirmed_issue(rule):
            return _pass_result(
                candidates,
                false_positive_count=_multi_gold_false_positive_count(candidates, rule, selector_resolutions),
            )
        return _evaluate_multi_gold_with_resolved_selectors(candidates, rule, selector_resolutions)

    gold_ids: set[str] = set()
    for selector in _gold_selectors(rule):
        gold_ids.update(_resolution_side(selector_resolutions, 'gold').get(selector, []))
    if not gold_ids:
        return evaluate_candidate_manifest(manifest, rule)

    if not _is_confirmed_issue(rule):
        false_positive_count = 0
        for candidate in candidates:
            candidate_ids = _candidate_resolved_ids(candidate, selector_resolutions)
            if _candidate_matches_gold_ids(candidate_ids, gold_ids) or _candidate_matches_gold_relation(candidate, _gold_selectors(rule), selector_resolutions):
                false_positive_count += 1
        return _pass_result(candidates, false_positive_count=false_positive_count)

    matched_ids: set[str] = set()
    matched_candidate_count = 0
    used_resolution_match = False
    used_relation_match = False
    for candidate in candidates:
        candidate_ids = _candidate_resolved_ids(candidate, selector_resolutions)
        resolution_match = _candidate_matches_gold_ids(candidate_ids, gold_ids)
        relation_ids = set() if resolution_match else _candidate_gold_relation_ids(candidate, _gold_selectors(rule), selector_resolutions)
        relation_match = bool(relation_ids)
        if relation_match or resolution_match:
            matched_candidate_count += 1
            matched_ids.update(candidate_ids & gold_ids)
            used_resolution_match = used_resolution_match or resolution_match
            used_relation_match = used_relation_match or relation_match
            matched_ids.update(relation_ids)

    if not matched_candidate_count:
        alias_result = evaluate_candidate_manifest(manifest, rule)
        if alias_result.get('matched_candidate_count'):
            return alias_result
    return _confirmed_result(
        candidates,
        gold_target_count=len(gold_ids),
        matched_target_count=len(matched_ids),
        matched_candidate_count=matched_candidate_count,
        match_basis=(
            'selector_resolution+selector_relation'
            if used_resolution_match and used_relation_match else
            'selector_resolution'
            if used_resolution_match else
            'selector_relation'
            if used_relation_match else
            None
        ),
    )


async def evaluate_candidate_manifest_on_page(
    *,
    page: Any,
    manifest: dict[str, Any],
    rule: dict[str, Any],
    task: dict[str, Any] | None = None,
    resolver: Any,
) -> dict[str, Any]:
    candidates = _manifest_candidates(manifest)
    candidate_selectors = [str(item.get('selector') or '').strip() for item in candidates]
    candidate_selectors = [selector for selector in candidate_selectors if selector]
    gold_selector_list = _gold_selectors(rule)
    gold_selector_group_list = _gold_selector_groups(rule)
    page_result = await resolver(
        page=page,
        task=task or {},
        rule=rule,
        gold_selector_list=gold_selector_list,
        gold_selector_group_list=gold_selector_group_list,
        agent_selector_list=candidate_selectors,
        timeout_ms=8000,
    )
    raw_resolutions = page_result.get('selector_resolutions') or {}
    selector_resolutions = {
        'gold': raw_resolutions.get('gold', {}),
        'candidate': raw_resolutions.get('candidate') or raw_resolutions.get('agent', {}),
        'relations': raw_resolutions.get('relations', {}),
    }
    result = evaluate_candidate_manifest_with_resolved_selectors(
        manifest,
        rule,
        selector_resolutions,
    )
    result['precondition_actions'] = page_result.get('precondition_actions', [])
    result['selector_errors'] = page_result.get('selector_errors', [])
    return result
