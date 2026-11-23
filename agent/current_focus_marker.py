from __future__ import annotations

import base64
import inspect
import re
import types
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Callable, Iterable

from PIL import Image, ImageDraw


MARKER_NOTE = 'Focus marker note: artificial, not page UI or page-provided visible focus.'


@dataclass(frozen=True)
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class FocusMarkerTarget:
    marker: str
    backend_node_id: int | None
    summary: str
    bbox: BoundingBox | None = None


class MarkedDOMState:
    def __init__(self, original: Any, targets: list[FocusMarkerTarget]):
        self._original = original._original if isinstance(original, MarkedDOMState) else original
        self._targets = targets

    def __getattr__(self, name: str) -> Any:
        return getattr(self._original, name)

    def llm_representation(self, include_attributes: list[str] | None = None) -> str:
        original = self._original.llm_representation
        try:
            text = original(include_attributes=include_attributes)
        except TypeError:
            text = original()
        return apply_focus_text_marker(text, self._targets)


def apply_focus_text_marker(text: str, targets: Iterable[FocusMarkerTarget]) -> str:
    target_list = [target for target in targets if target.summary]
    if not target_list:
        return text

    header_lines = [MARKER_NOTE]
    for target in target_list:
        label = 'Keyboard-current item' if target.marker == 'KEYBOARD_CURRENT' else 'Current focus'
        if target.backend_node_id is None:
            header_lines.append(f'{label}: not listed ({target.summary})')
        else:
            header_lines.append(f'{label}: [{target.backend_node_id}] {target.summary}')

    marked_lines = [_mark_line(line, target_list) for line in text.splitlines()]
    return '\n'.join(header_lines + marked_lines)


def _mark_line(line: str, targets: list[FocusMarkerTarget]) -> str:
    for target in targets:
        if target.backend_node_id is None:
            continue
        node_id = re.escape(str(target.backend_node_id))
        patterns = [
            r'^(\s*)((?:\|SHADOW\([^)]*\)\|)?\*?\[' + node_id + r'\])',
            r'^(\s*)((?:\|SHADOW\([^)]*\)\|)?\|scroll element\[' + node_id + r'\])',
        ]
        for pattern in patterns:
            if re.match(pattern, line):
                return re.sub(pattern, r'\1' + target.marker + r' \2', line, count=1)
    return line


def apply_focus_screenshot_marker(screenshot_b64: str, bbox: BoundingBox | None) -> str:
    if bbox is None or bbox.width <= 0 or bbox.height <= 0:
        return screenshot_b64
    try:
        raw = base64.b64decode(screenshot_b64)
        image = Image.open(BytesIO(raw)).convert('RGB')
    except Exception:
        return screenshot_b64

    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    left = max(0, int(round(bbox.x)) - 6)
    top = max(0, int(round(bbox.y)) - 6)
    right = min(image_width - 1, int(round(bbox.x + bbox.width)) + 6)
    bottom = min(image_height - 1, int(round(bbox.y + bbox.height)) + 6)
    if right <= left or bottom <= top:
        return screenshot_b64

    color = (217, 70, 239)
    _draw_dashed_rectangle(draw, (left, top, right, bottom), color=color, dash=8, gap=5, width=3)

    label = 'FOCUS MARKER'
    label_width = 78
    label_height = 12
    label_left = left
    label_top = max(0, top - label_height - 2)
    draw.rectangle((label_left, label_top, min(image_width - 1, label_left + label_width), label_top + label_height), fill=(255, 255, 255))
    draw.text((label_left + 2, label_top), label, fill=color)

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('ascii')


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


def install_current_focus_marker(
    browser_session: Any,
    focus_getter: Callable[[Any, Any], Any] | None = None,
) -> None:
    original = browser_session.get_browser_state_summary
    getter = focus_getter or get_current_focus_targets

    async def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
        state = await original(*args, **kwargs)
        try:
            targets = getter(self, state)
            if inspect.isawaitable(targets):
                targets = await targets
            target_list = list(targets or [])
        except Exception:
            return state
        if not target_list:
            return state
        state.dom_state = MarkedDOMState(state.dom_state, target_list)
        screenshot_target = next((target for target in target_list if target.marker == 'KEYBOARD_CURRENT' and target.bbox is not None), None)
        if screenshot_target is None:
            screenshot_target = next((target for target in target_list if target.bbox is not None), None)
        if screenshot_target is not None and getattr(state, 'screenshot', None):
            state.screenshot = apply_focus_screenshot_marker(state.screenshot, screenshot_target.bbox)
        return state

    object.__setattr__(browser_session, 'get_browser_state_summary', types.MethodType(wrapped, browser_session))


async def get_current_focus_targets(browser_session: Any, state: Any) -> list[FocusMarkerTarget]:
    cdp_session = await browser_session.get_or_create_cdp_session(target_id=None, focus=False)
    summary = await _evaluate_json(cdp_session, FOCUS_SUMMARY_JS)
    focus_payload = summary.get('focus') if isinstance(summary, dict) else None
    keyboard_payload = summary.get('keyboardCurrent') if isinstance(summary, dict) else None
    focus_backend_id = await _backend_node_id_for_expression(cdp_session, ACTIVE_ELEMENT_JS)
    keyboard_backend_id = None
    if isinstance(keyboard_payload, dict) and keyboard_payload.get('exists'):
        keyboard_backend_id = await _backend_node_id_for_expression(cdp_session, KEYBOARD_CURRENT_JS)

    targets: list[FocusMarkerTarget] = []
    focus_target = _target_from_payload(focus_payload, focus_backend_id, state, 'CURRENT_FOCUS')
    if focus_target:
        targets.append(focus_target)
    keyboard_target = _target_from_payload(keyboard_payload, keyboard_backend_id, state, 'KEYBOARD_CURRENT')
    if keyboard_target and keyboard_target.backend_node_id != (focus_target.backend_node_id if focus_target else None):
        targets.append(keyboard_target)
    return targets


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


def _target_from_payload(payload: dict[str, Any] | None, backend_node_id: int | None, state: Any, marker: str) -> FocusMarkerTarget | None:
    if not isinstance(payload, dict) or not payload.get('exists'):
        return None
    node = _selector_node(state, backend_node_id) if backend_node_id is not None else None
    tag = str(payload.get('tag') or '').lower()
    if node is None and tag in {'body', 'html'}:
        return None
    listed_id = backend_node_id if node is not None else None
    return FocusMarkerTarget(marker=marker, backend_node_id=listed_id, summary=_summary(payload, node), bbox=_bbox(payload.get('rect'), payload))


def _selector_node(state: Any, backend_node_id: int) -> Any | None:
    selector_map = getattr(getattr(state, 'dom_state', None), 'selector_map', None) or {}
    return selector_map.get(backend_node_id)


def _summary(fields: dict[str, Any], node: Any | None) -> str:
    attrs = getattr(node, 'attributes', {}) or {}
    tag = str(fields.get('tag') or getattr(node, 'tag_name', '') or 'element').lower()
    ident = fields.get('id') or attrs.get('id')
    role = fields.get('role') or attrs.get('role')
    label = fields.get('label') or _node_label(node)
    head = tag + (f'#{ident}' if ident else '')
    if role and role != tag:
        head += f' role={role}'
    if label:
        return f'{head} labeled {label}'
    return head


def _node_label(node: Any | None) -> str:
    if node is None:
        return ''
    attrs = getattr(node, 'attributes', {}) or {}
    for key in ('aria-label', 'title', 'placeholder', 'alt', 'value'):
        if attrs.get(key):
            return str(attrs[key]).strip()
    if hasattr(node, 'get_meaningful_text_for_llm'):
        return str(node.get_meaningful_text_for_llm()).strip()
    return ''


def _bbox(rect: dict[str, Any] | None, payload: dict[str, Any] | None = None) -> BoundingBox | None:
    if not isinstance(rect, dict):
        return None
    try:
        scale = float(rect.get('devicePixelRatio', (payload or {}).get('devicePixelRatio', 1)) or 1)
        return BoundingBox(float(rect['x']) * scale, float(rect['y']) * scale, float(rect['width']) * scale, float(rect['height']) * scale)
    except (KeyError, TypeError, ValueError):
        return None


FOCUS_SUMMARY_JS = (
    '(() => {'
    '  const describe = (el) => {'
    '    if (!el) return {exists: false};'
    '    const rect = el.getBoundingClientRect();'
    "    const label = el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('alt') || el.getAttribute('placeholder') || (el.innerText || el.value || '').trim().slice(0, 80);"
    '    return {'
    '      exists: true,'
    "      tag: (el.tagName || '').toLowerCase(),"
    "      id: el.id || '',"
    "      role: el.getAttribute('role') || '',"
    '      label,'
    '      rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height, devicePixelRatio: window.devicePixelRatio || 1}'
    '    };'
    '  };'
    '  const focus = document.activeElement;'
    "  const activeId = focus && focus.getAttribute ? focus.getAttribute('aria-activedescendant') : '';"
    '  const keyboardCurrent = activeId ? document.getElementById(activeId) : null;'
    '  return {focus: describe(focus), keyboardCurrent: describe(keyboardCurrent)};'
    '})()'
)

ACTIVE_ELEMENT_JS = 'document.activeElement'
KEYBOARD_CURRENT_JS = (
    '(() => {'
    '  const focus = document.activeElement;'
    "  const activeId = focus && focus.getAttribute ? focus.getAttribute('aria-activedescendant') : '';"
    '  return activeId ? document.getElementById(activeId) : null;'
    '})()'
)
