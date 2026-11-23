from __future__ import annotations

import base64
import inspect
import json
import re
import types
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Iterable

from PIL import Image, ImageDraw

from agent.current_focus_marker import BoundingBox


MARKER_NOTE = 'Evidence marker note: A11Y markers are artificial pointers, not page UI, not focus indicators, and not verdicts.'
PROMPT_LEGEND = (
    'Scoped evidence markers: A11Y-F*/A11Y-K* are artificial pointers to pre-collected suspect regions; '
    'they are not page UI, focus indicators, rankings, or verdicts. Verify before reporting.'
)

SELECTOR_SUMMARY_JS_TEMPLATE = r'''
(() => {
  let el = null;
  try { el = document.querySelector(__SELECTOR__); }
  catch (e) { return {exists: false, visible: false, error: 'selector_error'}; }
  if (!el) return {exists: false, visible: false, error: 'missing'};
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const hiddenStyle = cs.display === 'none' || cs.visibility === 'hidden';
  const emptyBox = r.width <= 0 || r.height <= 0;
  const offscreen = r.bottom <= 0 || r.right <= 0 || r.top >= innerHeight || r.left >= innerWidth;
  const label = el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('alt') || el.getAttribute('placeholder') || (el.innerText || el.value || '').trim().slice(0, 80);
  return {
    exists: true,
    visible: !(hiddenStyle || emptyBox || offscreen),
    count: 1,
    tag: (el.tagName || '').toLowerCase(),
    id: el.id || '',
    role: el.getAttribute('role') || '',
    label,
    rect: {x: r.x, y: r.y, width: r.width, height: r.height, devicePixelRatio: window.devicePixelRatio || 1}
  };
})()
'''


@dataclass(frozen=True)
class EvidenceCandidate:
    marker_id: str
    selector: str
    label: str
    family: str
    candidate_type: str
    evidence: str
    tab_index: int | None = None


@dataclass(frozen=True)
class EvidencePack:
    path: Path
    task_id: str
    instance_id: str
    family: str
    candidates: tuple[EvidenceCandidate, ...]


@dataclass(frozen=True)
class EvidenceMarkerTarget:
    marker_id: str
    backend_node_id: int | None
    summary: str
    bbox: BoundingBox | None
    family: str


@dataclass(frozen=True)
class MarkerResolution:
    targets: tuple[EvidenceMarkerTarget, ...]
    debug: dict[str, Any]


class EvidenceMarkedDOMState:
    def __init__(self, original: Any, targets: list[EvidenceMarkerTarget]):
        self._original = original._original if isinstance(original, EvidenceMarkedDOMState) else original
        self._targets = targets

    def __getattr__(self, name: str) -> Any:
        return getattr(self._original, name)

    def llm_representation(self, include_attributes: list[str] | None = None) -> str:
        original = self._original.llm_representation
        try:
            text = original(include_attributes=include_attributes)
        except TypeError:
            text = original()
        return apply_evidence_text_markers(text, self._targets)


def load_evidence_pack_manifest(
    path: str | Path,
    *,
    expected_task_id: str | None = None,
    expected_instance_id: str | None = None,
    expected_family: str | None = None,
) -> EvidencePack:
    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Evidence manifest root must be a JSON object: ' + str(manifest_path))

    task_id = _require_str(data, 'task_id', manifest_path)
    instance_id = _require_str(data, 'instance_id', manifest_path)
    family = _require_str(data, 'family', manifest_path)
    if expected_task_id and task_id != expected_task_id:
        raise ValueError(f'Evidence manifest task_id mismatch: expected {expected_task_id}, got {task_id}')
    if expected_instance_id and instance_id != expected_instance_id:
        raise ValueError(f'Evidence manifest instance_id mismatch: expected {expected_instance_id}, got {instance_id}')
    if expected_family and family != expected_family:
        raise ValueError(f'Evidence manifest family mismatch: expected {expected_family}, got {family}')

    raw_candidates = data.get('suspect_candidates')
    if not isinstance(raw_candidates, list):
        raise ValueError('Evidence manifest suspect_candidates must be a list: ' + str(manifest_path))
    candidates = tuple(
        _candidate_from_mapping(item, family=family, index=index)
        for index, item in enumerate(raw_candidates, start=1)
        if isinstance(item, dict)
    )
    if len(candidates) != len(raw_candidates):
        raise ValueError('Evidence manifest contains non-object candidates: ' + str(manifest_path))
    return EvidencePack(path=manifest_path, task_id=task_id, instance_id=instance_id, family=family, candidates=candidates)


def build_evidence_pack_prompt_suffix(pack: EvidencePack) -> str:
    lines = [PROMPT_LEGEND]
    if not pack.candidates:
        lines.append('Candidate markers: none.')
        return '\n'.join(lines)
    lines.append('Candidate markers, not ranked:')
    for candidate in pack.candidates:
        label = _truncate_inline(candidate.label or 'unlabeled target', 80)
        evidence = _truncate_inline(candidate.evidence, 120)
        lines.append(f'- {candidate.marker_id}: {label}; selector `{candidate.selector}`; evidence: {evidence}')
    return '\n'.join(lines)


def append_evidence_pack_prompt(prompt_text: str, pack: EvidencePack) -> str:
    return prompt_text.rstrip() + '\n\n' + build_evidence_pack_prompt_suffix(pack)


def apply_evidence_text_markers(text: str, targets: Iterable[EvidenceMarkerTarget]) -> str:
    target_list = [target for target in targets if target.marker_id]
    if not target_list:
        return text
    header_lines = [MARKER_NOTE]
    for target in target_list:
        if target.backend_node_id is None:
            header_lines.append(f'{target.marker_id}: {target.summary}')
        else:
            header_lines.append(f'{target.marker_id}: [{target.backend_node_id}] {target.summary}')
    marked_lines = [_mark_line(line, target_list) for line in text.splitlines()]
    return '\n'.join(header_lines + marked_lines)


def apply_evidence_screenshot_markers(screenshot_b64: str, targets: Iterable[EvidenceMarkerTarget]) -> str:
    target_list = [target for target in targets if target.bbox is not None]
    if not target_list:
        return screenshot_b64
    try:
        raw = base64.b64decode(screenshot_b64)
        image = Image.open(BytesIO(raw)).convert('RGB')
    except Exception:
        return screenshot_b64

    draw = ImageDraw.Draw(image)
    for target in target_list:
        _draw_marker(draw, image.size, target)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def install_evidence_assisted_observation(
    browser_session: Any,
    evidence_pack: EvidencePack,
    *,
    target_resolver: Callable[[Any, Any, EvidencePack], Any] | None = None,
    debug_jsonl_path: str | Path | None = None,
) -> None:
    original = browser_session.get_browser_state_summary
    resolver = target_resolver or resolve_evidence_marker_targets
    debug_path = Path(debug_jsonl_path) if debug_jsonl_path else None
    step_counter = {'value': 0}

    async def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        if kwargs.get('cached') is True:
            kwargs['cached'] = False
        state = await original(*args, **kwargs)
        step_counter['value'] += 1
        try:
            resolution = resolver(self, state, evidence_pack)
            if inspect.isawaitable(resolution):
                resolution = await resolution
            if isinstance(resolution, MarkerResolution):
                targets = list(resolution.targets)
                debug = dict(resolution.debug)
            else:
                targets = list(resolution or [])
                debug = {'target_count': len(targets)}
        except Exception as exc:
            _write_debug(debug_path, {'step': step_counter['value'], 'error': type(exc).__name__, 'message': str(exc)})
            return state

        _write_debug(debug_path, {'step': step_counter['value'], **debug})
        if not targets:
            return state
        state.dom_state = EvidenceMarkedDOMState(state.dom_state, targets)
        if getattr(state, 'screenshot', None):
            state.screenshot = apply_evidence_screenshot_markers(state.screenshot, targets)
        return state

    object.__setattr__(browser_session, 'get_browser_state_summary', types.MethodType(wrapped, browser_session))


async def resolve_evidence_marker_targets(browser_session: Any, state: Any, evidence_pack: EvidencePack) -> MarkerResolution:
    cdp_session = await browser_session.get_or_create_cdp_session(target_id=None, focus=False)
    selector_map = getattr(getattr(state, 'dom_state', None), 'selector_map', None) or {}
    targets: list[EvidenceMarkerTarget] = []
    unresolved: list[dict[str, str]] = []
    for candidate in evidence_pack.candidates:
        payload = await _evaluate_json(cdp_session, _selector_summary_js(candidate.selector))
        if not payload.get('exists') or not payload.get('visible'):
            unresolved.append({'marker_id': candidate.marker_id, 'selector': candidate.selector, 'reason': str(payload.get('error') or 'not_visible_or_missing')})
            continue
        backend_id = await _backend_node_id_for_expression(cdp_session, _selector_element_js(candidate.selector))
        listed_backend_id = backend_id if backend_id in selector_map else None
        targets.append(
            EvidenceMarkerTarget(
                marker_id=candidate.marker_id,
                backend_node_id=listed_backend_id,
                summary=_target_summary(candidate, payload),
                bbox=_bbox(payload.get('rect'), payload),
                family=candidate.family,
            )
        )
    return MarkerResolution(
        targets=tuple(targets),
        debug={
            'task_id': evidence_pack.task_id,
            'family': evidence_pack.family,
            'candidate_count': len(evidence_pack.candidates),
            'resolved_count': len(targets),
            'unresolved_count': len(unresolved),
            'unresolved': unresolved[:50],
        },
    )


def _candidate_from_mapping(item: dict[str, Any], *, family: str, index: int) -> EvidenceCandidate:
    prefix = 'A11Y-F' if family == 'visible_focus' else 'A11Y-K'
    marker_id = str(item.get('marker_id') or f'{prefix}{index}').strip()
    selector = str(item.get('selector') or item.get('keyboard_current_selector') or item.get('focus_owner_selector') or '').strip()
    if not selector:
        raise ValueError(f'Evidence candidate {marker_id} has no selector')
    tab_index = _int_or_none(item.get('tab_index'))
    return EvidenceCandidate(
        marker_id=marker_id,
        selector=selector,
        label=_candidate_label(item),
        family=family,
        candidate_type=str(item.get('candidate_type') or '').strip(),
        evidence=_candidate_evidence(item, family=family, tab_index=tab_index),
        tab_index=tab_index,
    )


def _candidate_label(item: dict[str, Any]) -> str:
    for key in ('label', 'text', 'ariaLabel', 'title', 'id', 'selector'):
        value = str(item.get(key) or '').strip()
        if value:
            return ' '.join(value.split())
    return 'unlabeled target'


def _candidate_evidence(item: dict[str, Any], *, family: str, tab_index: int | None) -> str:
    candidate_type = str(item.get('candidate_type') or '').strip()
    if family == 'visible_focus':
        prefix = f'Tab stop {tab_index}; ' if tab_index is not None else ''
        return prefix + 'visual review found no clear page-rendered focus indicator.'
    if candidate_type == 'arrow_unreachable':
        return 'Composite-widget child was not reached by limited arrow-key probing.'
    if candidate_type == 'scoped_order_anomaly':
        return 'Observed Tab order skipped the scoped widget before reaching it later.'
    return 'Visible or pointer-operable candidate was not observed in the Tab trace.'


def _require_str(data: dict[str, Any], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Evidence manifest {key} must be a non-empty string: {path}')
    return value.strip()


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _truncate_inline(value: str, max_len: int) -> str:
    text = ' '.join(str(value or '').split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + '...'


def _mark_line(line: str, targets: list[EvidenceMarkerTarget]) -> str:
    by_backend: dict[int, list[str]] = {}
    for target in targets:
        if target.backend_node_id is None:
            continue
        by_backend.setdefault(target.backend_node_id, []).append(target.marker_id)
    for backend_id, marker_ids in by_backend.items():
        node_id = re.escape(str(backend_id))
        patterns = [
            r'^(\s*)((?:(?:CURRENT_FOCUS|KEYBOARD_CURRENT|A11Y-[FK]\d+)\s+)*)(\*?\[' + node_id + r'\])',
            r'^(\s*)((?:(?:CURRENT_FOCUS|KEYBOARD_CURRENT|A11Y-[FK]\d+)\s+)*)(\|scroll element\[' + node_id + r'\])',
            r'^(\s*)((?:(?:CURRENT_FOCUS|KEYBOARD_CURRENT|A11Y-[FK]\d+)\s+)*)(\|SHADOW\([^)]*\)\|\*?\[' + node_id + r'\])',
        ]
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                existing_tokens = (match.group(2) or '').split()
                new_tokens = [marker_id for marker_id in marker_ids if marker_id not in existing_tokens]
                if not new_tokens:
                    return line
                return re.sub(pattern, r'\1' + ' '.join(new_tokens) + ' ' + r'\2\3', line, count=1)
    return line


def _draw_marker(draw: ImageDraw.ImageDraw, image_size: tuple[int, int], target: EvidenceMarkerTarget) -> None:
    bbox = target.bbox
    if bbox is None or bbox.width <= 0 or bbox.height <= 0:
        return
    image_width, image_height = image_size
    color = (245, 158, 11) if target.family == 'visible_focus' else (14, 165, 233)
    left = max(0, int(round(bbox.x)) - 5)
    top = max(0, int(round(bbox.y)) - 5)
    right = min(image_width - 1, int(round(bbox.x + bbox.width)) + 5)
    bottom = min(image_height - 1, int(round(bbox.y + bbox.height)) + 5)
    if right <= left or bottom <= top:
        return
    _draw_dashed_rectangle(draw, (left, top, right, bottom), color=color, dash=5, gap=4, width=2)

    label = target.marker_id
    label_width = max(48, len(label) * 7 + 8)
    label_height = 14
    label_left = min(max(0, left), max(0, image_width - label_width - 1))
    if top - label_height - 3 >= 0:
        label_top = top - label_height - 3
    else:
        label_top = min(image_height - label_height - 1, bottom + 3)
    draw.rectangle((label_left, label_top, label_left + label_width, label_top + label_height), fill=(17, 17, 17))
    draw.text((label_left + 3, label_top + 1), label, fill=color)


def _draw_dashed_rectangle(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    color: tuple[int, int, int],
    dash: int,
    gap: int,
    width: int,
) -> None:
    left, top, right, bottom = box
    _draw_dashed_line(draw, (left, top), (right, top), color=color, dash=dash, gap=gap, width=width)
    _draw_dashed_line(draw, (right, top), (right, bottom), color=color, dash=dash, gap=gap, width=width)
    _draw_dashed_line(draw, (right, bottom), (left, bottom), color=color, dash=dash, gap=gap, width=width)
    _draw_dashed_line(draw, (left, bottom), (left, top), color=color, dash=dash, gap=gap, width=width)


def _draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    color: tuple[int, int, int],
    dash: int,
    gap: int,
    width: int,
) -> None:
    x1, y1 = start
    x2, y2 = end
    horizontal = y1 == y2
    total = abs(x2 - x1) if horizontal else abs(y2 - y1)
    direction = 1 if (x2 - x1 if horizontal else y2 - y1) >= 0 else -1
    pos = 0
    while pos <= total:
        segment_end = min(total, pos + dash)
        if horizontal:
            draw.line((x1 + direction * pos, y1, x1 + direction * segment_end, y1), fill=color, width=width)
        else:
            draw.line((x1, y1 + direction * pos, x1, y1 + direction * segment_end), fill=color, width=width)
        pos += dash + gap


def _target_summary(candidate: EvidenceCandidate, payload: dict[str, Any]) -> str:
    tag = str(payload.get('tag') or 'element').lower()
    ident = str(payload.get('id') or '').strip()
    role = str(payload.get('role') or '').strip()
    label = _truncate_inline(candidate.label or str(payload.get('label') or ''), 80)
    head = tag + (f'#{ident}' if ident else '')
    if role and role != tag:
        head += f' role={role}'
    if label:
        return f'{head} labeled {label}'
    return head


def _bbox(rect: dict[str, Any] | None, payload: dict[str, Any] | None = None) -> BoundingBox | None:
    if not isinstance(rect, dict):
        return None
    try:
        scale = float(rect.get('devicePixelRatio', (payload or {}).get('devicePixelRatio', 1)) or 1)
        return BoundingBox(float(rect['x']) * scale, float(rect['y']) * scale, float(rect['width']) * scale, float(rect['height']) * scale)
    except (KeyError, TypeError, ValueError):
        return None


async def _evaluate_json(cdp_session: Any, expression: str) -> dict[str, Any]:
    result = await cdp_session.cdp_client.send.Runtime.evaluate(
        params={'expression': expression, 'returnByValue': True, 'awaitPromise': False},
        session_id=cdp_session.session_id,
    )
    value = result.get('result', {}).get('value') if isinstance(result, dict) else None
    return value if isinstance(value, dict) else {}


async def _backend_node_id_for_expression(cdp_session: Any, expression: str) -> int | None:
    result = await cdp_session.cdp_client.send.Runtime.evaluate(
        params={'expression': expression, 'returnByValue': False, 'awaitPromise': False},
        session_id=cdp_session.session_id,
    )
    object_id = result.get('result', {}).get('objectId') if isinstance(result, dict) else None
    if not object_id:
        return None
    try:
        node_info = await cdp_session.cdp_client.send.DOM.describeNode(
            params={'objectId': object_id},
            session_id=cdp_session.session_id,
        )
        backend_id = node_info.get('node', {}).get('backendNodeId') if isinstance(node_info, dict) else None
        return backend_id if isinstance(backend_id, int) else None
    finally:
        await _release_object(cdp_session, object_id)


async def _release_object(cdp_session: Any, object_id: str) -> None:
    try:
        await cdp_session.cdp_client.send.Runtime.releaseObject(
            params={'objectId': object_id},
            session_id=cdp_session.session_id,
        )
    except Exception:
        pass


def _selector_element_js(selector: str) -> str:
    selector_json = json.dumps(selector)
    return 'document.querySelector(' + selector_json + ')'


def _selector_summary_js(selector: str) -> str:
    return SELECTOR_SUMMARY_JS_TEMPLATE.replace('__SELECTOR__', json.dumps(selector))


def _write_debug(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=True, sort_keys=True)
            handle.write('\n')
    except Exception:
        pass
