from __future__ import annotations

import json
from typing import Any

Marker = dict[str, Any]


def build_marker_legend() -> str:
    return (
        'Experimental visual markers may appear on the page, labeled A11Y-F* or A11Y-K*.\n'
        'They mark pre-collected candidate regions for inspection.\n'
        'They are not page UI, not focus indicators, and not verdicts.\n'
        'Use them only as pointers to areas worth verifying.'
    )


def _safe_marker(marker: Marker) -> Marker:
    rect = marker.get('rect') or {}
    return {
        'marker_id': str(marker.get('marker_id') or marker.get('id') or ''),
        'label': str(marker.get('label') or marker.get('text') or marker.get('target') or ''),
        'rect': {
            'x': float(rect.get('x') or 0),
            'y': float(rect.get('y') or 0),
            'w': float(rect.get('w') or rect.get('width') or 0),
            'h': float(rect.get('h') or rect.get('height') or 0),
        },
    }


def build_marker_overlay_script(candidates: list[Marker]) -> str:
    markers = [_safe_marker(candidate) for candidate in candidates if candidate.get('rect')]
    marker_json = json.dumps(markers, ensure_ascii=False)
    q = chr(39)
    return (
        '(() => { const MARKERS = ' + marker_json + '; '
        f'const root = document.createElement({q}div{q}); '
        f'root.setAttribute({q}aria-hidden{q}, {q}true{q}); '
        f'root.style.pointerEvents = {q}none{q}; '
        f'root.style.position = {q}absolute{q}; root.style.left = {q}0{q}; root.style.top = {q}0{q}; '
        f'root.style.zIndex = {q}2147483647{q}; '
        'for (const marker of MARKERS) { '
        f'const badge = document.createElement({q}div{q}); '
        f'badge.setAttribute({q}aria-hidden{q}, {q}true{q}); '
        'badge.textContent = marker.marker_id; '
        f'badge.style.pointerEvents = {q}none{q}; '
        f'badge.style.position = {q}absolute{q}; '
        'badge.style.left = `${marker.rect.x}px`; badge.style.top = `${marker.rect.y}px`; '
        f'badge.style.padding = {q}2px 4px{q}; badge.style.font = {q}12px sans-serif{q}; '
        f'badge.style.color = {q}#fff{q}; badge.style.background = {q}#111{q}; '
        f'badge.style.borderRadius = {q}3px{q}; '
        'root.appendChild(badge); } '
        'document.documentElement.appendChild(root); })();'
    )
