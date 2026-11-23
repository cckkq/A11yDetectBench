from __future__ import annotations

import inspect
import io
from typing import Any
from pathlib import Path

from PIL import Image, ImageChops

from agent.evidence_baseline.candidates import select_focus_visible_suspects


INJECT_FOCUS_LISTENER_JS = '''(() => {
  window.__a11yFocusEvidenceData = [];
  window.__a11yFocusEvidenceFirstFocused = null;
  window.__a11yFocusEvidencePreFocus = null;
  function selectorFor(el) {
    if (!el || !el.tagName) return '';
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el !== document.body && el !== document.documentElement) {
      let part = el.tagName.toLowerCase();
      const parent = el.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((node) => node.tagName === el.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')';
      }
      parts.unshift(part);
      el = parent;
    }
    return parts.join(' > ');
  }
  function styleFor(el) {
    const s = el && window.getComputedStyle ? window.getComputedStyle(el) : {};
    return {outline: s.outline || '', boxShadow: s.boxShadow || '', border: s.border || '', backgroundColor: s.backgroundColor || ''};
  }
  function elementInfo(el) {
    if (!el || !el.tagName) return null;
    return {selector: selectorFor(el), id: el.id || '', tag: el.tagName || '', style: styleFor(el)};
  }
  document.addEventListener('keydown', () => {
    window.__a11yFocusEvidencePreFocus = elementInfo(document.activeElement);
  }, true);
  document.addEventListener('focusin', (event) => {
    const el = event.target;
    if (!window.__a11yFocusEvidenceFirstFocused && el !== document.body) window.__a11yFocusEvidenceFirstFocused = el;
    const r = el && el.getBoundingClientRect ? el.getBoundingClientRect() : {x:0,y:0,width:0,height:0};
    const computedStyle = styleFor(el);
    const before = window.__a11yFocusEvidencePreFocus;
    const beforeStyle = before && before.selector === selectorFor(el) ? before.style : null;
    window.__a11yFocusEvidenceData.push({
      tab_index: window.__a11yFocusEvidenceData.length + 1,
      tag: el ? el.tagName : 'BODY', id: el ? (el.id || '') : '', role: el && el.getAttribute ? (el.getAttribute('role') || '') : '',
      text: el ? (el.textContent || '').trim().slice(0,80) : '', ariaLabel: el && el.getAttribute ? (el.getAttribute('aria-label') || '') : '',
      title: el && el.getAttribute ? (el.getAttribute('title') || '') : '', href: el && el.href ? el.href.slice(0,160) : '',
      selector: selectorFor(el),
      rect: {x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height)},
      before_computed_style: beforeStyle,
      computed_style: computedStyle,
      visual_delta: 'uncertain',
      style_delta: {}
    });
  }, true);
  return 'a11y focus evidence listener injected';
})()'''


CHECK_FOCUS_STATUS_JS = '''(() => {
  const el = document.activeElement;
  const data = window.__a11yFocusEvidenceData ? window.__a11yFocusEvidenceData : [];
  const isBody = !el || el === document.body || el === document.documentElement;
  const isBack = Boolean(window.__a11yFocusEvidenceFirstFocused && el === window.__a11yFocusEvidenceFirstFocused && data.length > 1);
  return {isBody, isBack, count: data.length, currentTag: el ? el.tagName : 'null', currentId: el ? (el.id || '') : ''};
})()'''


GET_FOCUS_DATA_JS = '''() => window.__a11yFocusEvidenceData || []'''


GET_CURRENT_FOCUS_OBSERVATION_JS = '''(() => {
  'GET_A11Y_CURRENT_FOCUS_OBSERVATION';
  const active = document.activeElement;
  if (!active || active === document.body || active === document.documentElement) return null;
  function selectorFor(el) {
    if (!el || !el.tagName) return '';
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el !== document.body && el !== document.documentElement) {
      let part = el.tagName.toLowerCase();
      const parent = el.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((node) => node.tagName === el.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')';
      }
      parts.unshift(part);
      el = parent;
    }
    return parts.join(' > ');
  }
  function visible(el) {
    if (!el || el.hidden || el.getAttribute('aria-hidden') === 'true') return false;
    const s = window.getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function styleFor(el) {
    const s = el && window.getComputedStyle ? window.getComputedStyle(el) : {};
    return {
      outline: s.outline || '',
      outlineColor: s.outlineColor || '',
      outlineStyle: s.outlineStyle || '',
      outlineWidth: s.outlineWidth || '',
      boxShadow: s.boxShadow || '',
      border: s.border || '',
      borderColor: s.borderColor || '',
      borderStyle: s.borderStyle || '',
      borderWidth: s.borderWidth || '',
      backgroundColor: s.backgroundColor || '',
      color: s.color || '',
    };
  }
  function rectFor(el) {
    const r = el && el.getBoundingClientRect ? el.getBoundingClientRect() : {x:0,y:0,width:0,height:0};
    return {
      x: Math.round(r.x + window.scrollX),
      y: Math.round(r.y + window.scrollY),
      w: Math.round(r.width),
      h: Math.round(r.height),
      viewportX: Math.round(r.x),
      viewportY: Math.round(r.y),
    };
  }
  function labelText(el) {
    if (!el) return '';
    return (el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent || '').trim().slice(0, 120);
  }
  function infoFor(el) {
    if (!el || !el.tagName) return null;
    return {
      selector: selectorFor(el),
      id: el.id || '',
      tag: el.tagName || '',
      role: el.getAttribute('role') || '',
      text: (el.textContent || '').trim().slice(0, 120),
      ariaLabel: el.getAttribute('aria-label') || '',
      title: el.getAttribute('title') || '',
      href: el.href ? el.href.slice(0, 160) : '',
      rect: rectFor(el),
      computed_style: styleFor(el),
    };
  }
  const focusOwner = active;
  const activeDescendantId = focusOwner.getAttribute('aria-activedescendant') || '';
  let keyboardCurrent = null;
  if (activeDescendantId) {
    try { keyboardCurrent = document.getElementById(activeDescendantId); } catch { keyboardCurrent = null; }
  }
  let target = focusOwner;
  let source = 'active_element';
  if (keyboardCurrent && visible(keyboardCurrent)) {
    target = keyboardCurrent;
    source = 'aria_activedescendant';
  }
  const targetInfo = infoFor(target);
  const ownerInfo = infoFor(focusOwner);
  if (!targetInfo || !ownerInfo) return null;
  const data = window.__a11yFocusEvidenceData || [];
  return {
    ...targetInfo,
    tab_index: data.length || 1,
    label: labelText(target),
    focus_owner_selector: ownerInfo.selector,
    focus_owner_id: ownerInfo.id,
    focus_owner_tag: ownerInfo.tag,
    focus_owner_role: ownerInfo.role,
    focus_owner_rect: ownerInfo.rect,
    focus_owner_computed_style: ownerInfo.computed_style,
    active_descendant_id: activeDescendantId,
    keyboard_current_source: source,
    keyboard_current_selector: targetInfo.selector,
    before_computed_style: null,
    visual_delta: 'uncertain',
    style_delta: {},
  };
})()'''


GET_FOCUS_STYLE_SNAPSHOT_JS = '''(() => {
  const selectors = `a[href], button, input:not([type='hidden']), select, textarea, [tabindex]:not([tabindex='-1']), [role='button'], [role='link'], [role='menuitem'], [role='tab'], [contenteditable='true']`;
  function selectorFor(el) {
    if (!el || !el.tagName) return '';
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    while (el && el !== document.body && el !== document.documentElement) {
      let part = el.tagName.toLowerCase();
      const parent = el.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((node) => node.tagName === el.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(el) + 1) + ')';
      }
      parts.unshift(part);
      el = parent;
    }
    return parts.join(' > ');
  }
  function visible(el) {
    if (!el || el.hidden || el.disabled || el.getAttribute('aria-hidden') === 'true') return false;
    const s = window.getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function styleFor(el) {
    const s = window.getComputedStyle(el);
    return {outline: s.outline || '', boxShadow: s.boxShadow || '', border: s.border || '', backgroundColor: s.backgroundColor || ''};
  }
  const items = Array.from(document.querySelectorAll(selectors)).filter(visible).map((el) => ({
    selector: selectorFor(el),
    id: el.id || '',
    tag: el.tagName || '',
    text: (el.textContent || '').trim().slice(0,80),
    ariaLabel: el.getAttribute('aria-label') || '',
    title: el.getAttribute('title') || '',
    computed_style: styleFor(el),
  }));
  return {next_tab_index: (window.__a11yFocusEvidenceData || []).length + 1, items};
})()'''


def _with_focus_marker_ids(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marked: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        item.setdefault('marker_id', f'A11Y-F{index}')
        item.setdefault('label', item.get('ariaLabel') or item.get('text') or item.get('id') or item.get('role') or '')
        marked.append(item)
    return marked


def _style_value(style: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = style.get(key)
        if value is not None:
            return str(value).strip().lower()
    return ''


def _style_changed(before: dict[str, Any], after: dict[str, Any], *keys: str) -> bool:
    return _style_value(before, *keys) != _style_value(after, *keys)


def _has_clear_focus_style(style: dict[str, Any]) -> bool:
    outline = str(style.get('outline') or '').strip().lower()
    box_shadow = str(style.get('boxShadow') or style.get('box_shadow') or '').strip().lower()
    border = str(style.get('border') or '').strip().lower()
    background = str(style.get('backgroundColor') or style.get('background_color') or '').strip().lower()
    if outline and ' none ' not in f' {outline} ' and not outline.endswith(' 0px'):
        return True
    if box_shadow and box_shadow != 'none':
        return True
    if border and '0px' not in border and 'transparent' not in border and 'rgba(0, 0, 0, 0)' not in border:
        return True
    if background and background not in {'transparent', 'rgba(0, 0, 0, 0)'}:
        return True
    return False


def _enrich_focus_observation_with_style_delta(observation: dict[str, Any]) -> dict[str, Any]:
    before = observation.get('before_computed_style') or {}
    after = observation.get('computed_style') or {}
    if not isinstance(before, dict) or not isinstance(after, dict) or not before:
        return dict(observation)
    style_delta = {
        'outline_changed': _style_changed(before, after, 'outline'),
        'box_shadow_changed': _style_changed(before, after, 'boxShadow', 'box_shadow'),
        'border_changed': _style_changed(before, after, 'border'),
        'background_changed': _style_changed(before, after, 'backgroundColor', 'background_color'),
    }
    enriched = dict(observation)
    enriched['style_delta'] = style_delta
    if any(style_delta.values()) and _has_clear_focus_style(after):
        enriched['visual_delta'] = 'clear_indicator'
    elif not any(style_delta.values()) and str(enriched.get('visual_delta') or '') == 'uncertain':
        enriched['visual_delta'] = 'none_observed'
    return enriched


def _snapshot_match_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get('tag') or '').strip().lower(),
        str(item.get('id') or '').strip().lower(),
        str(item.get('text') or '').strip().lower(),
    )


def _find_before_style_snapshot(observation: dict[str, Any], snapshots: list[dict[str, Any]]) -> dict[str, Any] | None:
    selectors = [
        str(observation.get('selector') or '').strip(),
        str(observation.get('keyboard_current_selector') or '').strip(),
        str(observation.get('focus_owner_selector') or '').strip(),
    ]
    for selector in [item for item in selectors if item]:
        for item in snapshots:
            if str(item.get('selector') or '').strip() == selector:
                style = item.get('computed_style')
                return style if isinstance(style, dict) else None
    obs_id = str(observation.get('id') or '').strip()
    if obs_id:
        for item in snapshots:
            if str(item.get('id') or '').strip() == obs_id:
                style = item.get('computed_style')
                return style if isinstance(style, dict) else None
    obs_key = _snapshot_match_key(observation)
    for item in snapshots:
        if _snapshot_match_key(item) == obs_key:
            style = item.get('computed_style')
            return style if isinstance(style, dict) else None
    return None


def _merge_focus_before_style_snapshots(
    observations: list[dict[str, Any]],
    before_style_snapshots: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for observation in observations:
        item = dict(observation)
        tab_index = int(item.get('tab_index') or 0)
        if not isinstance(item.get('before_computed_style'), dict):
            before_style = _find_before_style_snapshot(item, before_style_snapshots.get(tab_index, []))
            if before_style is not None:
                item['before_computed_style'] = before_style
        merged.append(_enrich_focus_observation_with_style_delta(item))
    return merged


def _write_focus_artifact_files(
    artifacts_dir: Path,
    observation: dict[str, Any],
    before_png: bytes,
    after_png: bytes,
    *,
    crop_padding: int = 150,
    classification_crop_padding: int = 2,
) -> dict[str, Any]:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    tab_index = int(observation.get('tab_index') or 0)
    before_path = artifacts_dir / f'focus_{tab_index:04d}_before.png'
    after_path = artifacts_dir / f'focus_{tab_index:04d}_after.png'
    before_crop_path = artifacts_dir / f'focus_{tab_index:04d}_before_crop.png'
    after_crop_path = artifacts_dir / f'focus_{tab_index:04d}_after_crop.png'
    before_path.write_bytes(before_png)
    after_path.write_bytes(after_png)
    before_crop = _crop_png_around_rect(before_png, observation.get('rect') or {}, crop_padding)
    after_crop = _crop_png_around_rect(after_png, observation.get('rect') or {}, crop_padding)
    before_classification_crop = _crop_png_around_rect(before_png, observation.get('rect') or {}, classification_crop_padding)
    after_classification_crop = _crop_png_around_rect(after_png, observation.get('rect') or {}, classification_crop_padding)
    before_crop_path.write_bytes(before_crop)
    after_crop_path.write_bytes(after_crop)
    pixel_visual_delta = _classify_focus_visual_delta_from_pngs(before_classification_crop, after_classification_crop)
    enriched = dict(observation)
    enriched.update({
        'before_screenshot_path': str(before_path),
        'after_screenshot_path': str(after_path),
        'before_crop_path': str(before_crop_path),
        'after_crop_path': str(after_crop_path),
        'crop_padding': crop_padding,
        'classification_crop_padding': classification_crop_padding,
        'pixel_visual_delta': pixel_visual_delta,
    })
    existing_visual_delta = str(enriched.get('visual_delta') or '').strip().lower()
    if pixel_visual_delta == 'clear_indicator' or (pixel_visual_delta == 'none_observed' and existing_visual_delta not in {'clear_indicator', 'visible_delta_observed'}):
        enriched['visual_delta'] = pixel_visual_delta
    return enriched


def _crop_png_around_rect(image_bytes: bytes, rect: dict[str, Any], padding: int) -> bytes:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except Exception:
        return image_bytes
    width, height = image.size
    x = float(rect.get('x') or 0)
    y = float(rect.get('y') or 0)
    w = float(rect.get('w') or rect.get('width') or 0)
    h = float(rect.get('h') or rect.get('height') or 0)
    if w <= 0 or h <= 0:
        return image_bytes
    left = max(0, int(round(x)) - padding)
    top = max(0, int(round(y)) - padding)
    right = min(width, int(round(x + w)) + padding)
    bottom = min(height, int(round(y + h)) + padding)
    if right <= left or bottom <= top:
        return image_bytes
    output = io.BytesIO()
    image.crop((left, top, right, bottom)).save(output, format='PNG')
    return output.getvalue()


def _classify_focus_visual_delta_from_pngs(before_png: bytes, after_png: bytes) -> str:
    try:
        before = Image.open(io.BytesIO(before_png)).convert('RGB')
        after = Image.open(io.BytesIO(after_png)).convert('RGB')
        before.load()
        after.load()
    except Exception:
        return 'uncertain'
    if before.size != after.size or before.width <= 0 or before.height <= 0:
        return 'uncertain'

    diff = ImageChops.difference(before, after)
    total_pixels = before.width * before.height
    changed_pixels = 0
    total_delta = 0
    histogram = diff.convert('L').histogram()
    for value, count in enumerate(histogram):
        total_delta += value * count
        if value >= 8:
            changed_pixels += count
    changed_ratio = changed_pixels / float(total_pixels)
    mean_delta = total_delta / float(total_pixels)
    if changed_ratio <= 0.001 and mean_delta < 0.5:
        return 'none_observed'
    if changed_ratio >= 0.01 or mean_delta >= 2.0:
        return 'clear_indicator'
    return 'uncertain'


async def _maybe_review_focus_observations(
    observations: list[dict[str, Any]],
    vlm_reviewer: Any,
) -> list[dict[str, Any]]:
    if vlm_reviewer is None or not observations:
        return observations
    review_result = vlm_reviewer(observations)
    if inspect.isawaitable(review_result):
        review_result = await review_result
    review_by_tab = {int(item.get('tab_index') or 0): item for item in (review_result or [])}
    merged: list[dict[str, Any]] = []
    for observation in observations:
        item = dict(observation)
        review = review_by_tab.get(int(item.get('tab_index') or 0))
        if review:
            item['vlm_review'] = dict(review)
            indicator = str(review.get('visual_focus_indicator') or '').strip().lower()
            if indicator == 'absent':
                item['visual_delta'] = 'none_observed'
            elif indicator == 'present':
                item['visual_delta'] = 'clear_indicator'
            elif indicator == 'uncertain':
                item['visual_delta'] = 'uncertain'
            elif review.get('visual_delta'):
                item['visual_delta'] = review.get('visual_delta')
        merged.append(item)
    return merged


async def collect_focus_visible_candidates(
    page: Any,
    *,
    target_description: str = '',
    max_tabs: int = 300,
    tab_interval_ms: int = 200,
    artifacts_dir: Path | None = None,
    vlm_reviewer: Any = None,
) -> dict[str, Any]:
    await page.evaluate(INJECT_FOCUS_LISTENER_JS)
    stop_reason = 'max_tabs_reached'
    consecutive_body = 0
    tab_press_count = 0
    screenshot_pairs: dict[int, tuple[bytes, bytes]] = {}
    before_style_snapshots: dict[int, list[dict[str, Any]]] = {}
    observations_by_tab: dict[int, dict[str, Any]] = {}

    for tab_press_count in range(1, max_tabs + 1):
        style_snapshot = await page.evaluate(GET_FOCUS_STYLE_SNAPSHOT_JS)
        if isinstance(style_snapshot, dict):
            next_tab_index = int(style_snapshot.get('next_tab_index') or tab_press_count)
            before_style_snapshots[next_tab_index] = list(style_snapshot.get('items') or [])
        before_png = b''
        if artifacts_dir is not None:
            before_png = await page.screenshot(type='png', full_page=True)
        await page.keyboard.press('Tab')
        if tab_interval_ms > 0:
            await page.wait_for_timeout(tab_interval_ms)
        after_png = b''
        if artifacts_dir is not None:
            after_png = await page.screenshot(type='png', full_page=True)
            screenshot_pairs[tab_press_count] = (before_png, after_png)
        status = await page.evaluate(CHECK_FOCUS_STATUS_JS)
        if status.get('isBack'):
            stop_reason = 'cycle_complete'
            break
        if status.get('isBody'):
            consecutive_body += 1
            if consecutive_body >= 3:
                stop_reason = 'focus_lost_to_body'
                break
        else:
            consecutive_body = 0
        current_observation = await page.evaluate(GET_CURRENT_FOCUS_OBSERVATION_JS)
        if isinstance(current_observation, dict):
            observed_tab_index = int(current_observation.get('tab_index') or tab_press_count)
            observations_by_tab[observed_tab_index] = current_observation
            if artifacts_dir is not None and tab_press_count in screenshot_pairs:
                screenshot_pairs[observed_tab_index] = screenshot_pairs[tab_press_count]

    raw_observations = [observations_by_tab[key] for key in sorted(observations_by_tab)]
    if not raw_observations:
        raw_observations = await page.evaluate(GET_FOCUS_DATA_JS) or []
    observations = _merge_focus_before_style_snapshots(raw_observations, before_style_snapshots)
    if artifacts_dir is not None:
        enriched_observations = []
        for observation in observations:
            pair = screenshot_pairs.get(int(observation.get('tab_index') or 0))
            if pair:
                enriched_observations.append(
                    _write_focus_artifact_files(artifacts_dir, observation, pair[0], pair[1])
                )
            else:
                enriched_observations.append(observation)
        observations = enriched_observations
    observations = await _maybe_review_focus_observations(observations, vlm_reviewer)
    suspect_candidates = _with_focus_marker_ids(
        select_focus_visible_suspects(observations)
    )

    return {
        'family': 'visible_focus',
        'collection_method': 'real_tab_trace_plus_keyboard_current_visual_crops_vlm_first' if vlm_reviewer is not None else 'real_tab_trace_plus_focus_style_observations_fallback',
        'vlm_enabled': vlm_reviewer is not None,
        'target_description': target_description,
        'stop_reason': stop_reason,
        'max_tabs': max_tabs,
        'tab_interval_ms': tab_interval_ms,
        'tab_presses': tab_press_count,
        'artifacts_dir': str(artifacts_dir) if artifacts_dir is not None else None,
        'observations': observations,
        'suspect_candidates': suspect_candidates,
    }
