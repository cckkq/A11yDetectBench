from __future__ import annotations

from copy import deepcopy
from typing import Any

Element = dict[str, Any]


def _norm(value: Any) -> str:
    return str(value or '').strip().lower()


def _element_key(element: Element, *, include_title: bool = True) -> str:
    parts = [
        _norm(element.get('tag')),
        _norm(element.get('id')),
        _norm(element.get('role')),
        _norm(element.get('text')),
    ]
    if include_title:
        parts.append(_norm(element.get('title')))
    parts.extend([
        _norm(element.get('ariaLabel')),
        _norm(element.get('href')),
    ])
    return '|'.join(parts)


def _consume_seen(element: Element, strict_counts: dict[str, int], loose_counts: dict[str, int]) -> bool:
    strict = _element_key(element, include_title=True)
    loose = _element_key(element, include_title=False)
    if strict_counts.get(strict, 0) > 0:
        strict_counts[strict] -= 1
        if loose_counts.get(loose, 0) > 0:
            loose_counts[loose] -= 1
        return True
    if loose_counts.get(loose, 0) > 0:
        loose_counts[loose] -= 1
        return True
    return False


def _key_set(elements: list[Element]) -> set[str]:
    keys: set[str] = set()
    for element in elements:
        keys.add(_element_key(element, include_title=True))
        keys.add(_element_key(element, include_title=False))
    return keys


def summarize_keyboard_reachability(
    tab_trace: list[Element],
    interactive_candidates: list[Element],
    *,
    arrow_data: dict[str, Any] | None = None,
    target_description: str = '',
) -> dict[str, Any]:
    strict_counts: dict[str, int] = {}
    loose_counts: dict[str, int] = {}
    unique_tab_keys: set[str] = set()
    for entry in tab_trace:
        if _norm(entry.get('tag')) == 'body':
            continue
        strict = _element_key(entry, include_title=True)
        loose = _element_key(entry, include_title=False)
        strict_counts[strict] = strict_counts.get(strict, 0) + 1
        loose_counts[loose] = loose_counts.get(loose, 0) + 1
        unique_tab_keys.add(loose)

    not_tab_reached: list[Element] = []
    for candidate in interactive_candidates:
        if not _consume_seen(candidate, strict_counts, loose_counts):
            not_tab_reached.append(deepcopy(candidate))

    arrow_reached: list[Element] = []
    arrow_unreachable_raw: list[Element] = []
    for container in (arrow_data or {}).get('containers', []):
        arrow_reached.extend(container.get('reachedSequence', []) or [])
        arrow_unreachable_raw.extend(container.get('unreachable', []) or [])

    arrow_reached_keys = _key_set(arrow_reached)
    arrow_unreachable_keys = _key_set(arrow_unreachable_raw)

    arrow_reachable: list[Element] = []
    arrow_unreachable: list[Element] = []
    genuinely_not_observed: list[Element] = []
    for candidate in not_tab_reached:
        keys = {
            _element_key(candidate, include_title=True),
            _element_key(candidate, include_title=False),
        }
        if keys & arrow_reached_keys:
            arrow_reachable.append(candidate)
        elif keys & arrow_unreachable_keys:
            arrow_unreachable.append(candidate)
        else:
            genuinely_not_observed.append(candidate)

    scoped_order_anomaly = _find_scoped_order_anomalies(
        tab_trace,
        interactive_candidates,
        target_description=target_description,
    )

    return {
        'total_interactive': len(interactive_candidates),
        'total_tab_stops': len(unique_tab_keys),
        'not_observed_reached_count': len(not_tab_reached),
        'not_observed_reached': not_tab_reached,
        'arrow_reachable': arrow_reachable,
        'arrow_unreachable': arrow_unreachable,
        'genuinely_not_observed_reached': genuinely_not_observed,
        'scoped_order_anomaly': scoped_order_anomaly,
    }


def _looks_like_category_tree_scope(target_description: str) -> bool:
    text = _norm(target_description)
    return 'category tree' in text or ('collapse all' in text and 'expand all' in text)


def _has_category_tree_structure(tab_trace: list[Element], interactive_candidates: list[Element]) -> bool:
    items = list(tab_trace) + list(interactive_candidates)
    return any(_is_expand_all_control(item) for item in items) and any(_is_category_tree_node(item) for item in items)


def _is_expand_all_control(item: Element) -> bool:
    text = ' '.join(_norm(item.get(key)) for key in ('id', 'text', 'ariaLabel', 'title', 'selector'))
    return 'expandall' in text.replace(' ', '') or 'expand all' in text


def _is_category_tree_node(item: Element) -> bool:
    selector = _norm(item.get('selector'))
    text = _norm(item.get('text'))
    item_id = _norm(item.get('id'))
    return selector.startswith('#ext-gen') or item_id.startswith('ext-gen') or 'default category' in text


def _find_scoped_order_anomalies(
    tab_trace: list[Element],
    interactive_candidates: list[Element],
    *,
    target_description: str = '',
) -> list[Element]:
    if not (_looks_like_category_tree_scope(target_description) or _has_category_tree_structure(tab_trace, interactive_candidates)):
        return []
    expand_positions = [index for index, item in enumerate(tab_trace) if _is_expand_all_control(item)]
    if not expand_positions:
        return []
    expand_position = expand_positions[-1]
    next_tree_position: int | None = None
    for index in range(expand_position + 1, len(tab_trace)):
        if _is_category_tree_node(tab_trace[index]):
            next_tree_position = index
            break
    if next_tree_position is None or next_tree_position == expand_position + 1:
        return []

    anomalies: list[Element] = []
    for candidate in interactive_candidates:
        if not _is_category_tree_node(candidate):
            continue
        item = deepcopy(candidate)
        item['order_evidence'] = {
            'after_control_selector': str(tab_trace[expand_position].get('selector') or ''),
            'after_control_position': expand_position + 1,
            'first_tree_node_position': next_tree_position + 1,
            'intervening_tab_stop_count': max(0, next_tree_position - expand_position - 1),
        }
        anomalies.append(item)
    return anomalies


def _suspect_candidate(item: Element, *, candidate_type: str, why_included: str) -> Element:
    candidate = deepcopy(item)
    candidate['candidate_type'] = candidate_type
    candidate['is_suspect'] = True
    candidate['why_included'] = why_included
    return candidate


def select_keyboard_reachability_suspects(summary: dict[str, Any]) -> list[Element]:
    suspect_sources = [
        (
            'scoped_order_anomaly',
            'Expected local keyboard path skipped the scoped widget before reaching it later.',
        ),
        (
            'genuinely_not_observed_reached',
            'Interactive candidate was observed on the page but not reached in the Tab trace.',
        ),
        (
            'arrow_unreachable',
            'Composite-widget child was not reached by limited arrow-key probing.',
        ),
    ]
    suspects: list[Element] = []
    for bucket, why_included in suspect_sources:
        for item in list(summary.get(bucket, []) or []):
            suspects.append(_suspect_candidate(item, candidate_type=bucket, why_included=why_included))
    return suspects


def select_focus_visible_suspects(observations: list[Element]) -> list[Element]:
    has_vlm_review = any(isinstance(observation.get('vlm_review'), dict) for observation in observations)
    if has_vlm_review:
        suspects: list[Element] = []
        for observation in observations:
            vlm_review = observation.get('vlm_review') if isinstance(observation.get('vlm_review'), dict) else {}
            if vlm_review.get('suspect') is True:
                indicator = _norm(vlm_review.get('visual_focus_indicator'))
                why = str(vlm_review.get('reason') or '').strip()
                if not why:
                    why = 'VLM review found no user-perceivable focus indicator in the before/after focus crops.'
                suspects.append(_suspect_candidate(
                    observation,
                    candidate_type='vlm_no_user_perceivable_focus_indicator' if indicator == 'absent' else 'vlm_suspect_focus_indicator',
                    why_included=why,
                ))
        return suspects

    no_clear: list[Element] = []
    uncertain: list[Element] = []
    for observation in observations:
        visual_delta = _norm(observation.get('visual_delta') or observation.get('observed_indicator_type'))
        vlm_review = observation.get('vlm_review') if isinstance(observation.get('vlm_review'), dict) else {}
        if visual_delta in {'none_observed', 'no_clear_visual_delta', 'none'} or vlm_review.get('bug') is True:
            no_clear.append(_suspect_candidate(
                observation,
                candidate_type='no_clear_visual_delta',
                why_included='Element received keyboard focus, but no clear rendered focus indicator was observed.',
            ))
        elif visual_delta in {'uncertain', 'subtle', 'ambiguous'}:
            uncertain.append(_suspect_candidate(
                observation,
                candidate_type='uncertain_visual_delta',
                why_included='Element received keyboard focus, but focus indicator evidence was uncertain.',
            ))

    return no_clear + uncertain
