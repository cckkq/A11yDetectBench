from __future__ import annotations

from typing import Any

from agent.evidence_baseline.candidates import select_keyboard_reachability_suspects, summarize_keyboard_reachability


INJECT_TAB_LISTENER_JS = '''(() => {
  window.__a11yEvidenceTabData = [];
  window.__a11yEvidenceFirstFocused = null;
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
  document.addEventListener('focusin', (event) => {
    const el = event.target;
    if (!window.__a11yEvidenceFirstFocused && el !== document.body) window.__a11yEvidenceFirstFocused = el;
    const r = el && el.getBoundingClientRect ? el.getBoundingClientRect() : {x:0,y:0,width:0,height:0};
    window.__a11yEvidenceTabData.push({
      tag: el ? el.tagName : 'BODY', id: el ? (el.id || '') : '', role: el && el.getAttribute ? (el.getAttribute('role') || '') : '',
      text: el ? (el.textContent || '').trim().slice(0,80) : '', ariaLabel: el && el.getAttribute ? (el.getAttribute('aria-label') || '') : '',
      title: el && el.getAttribute ? (el.getAttribute('title') || '') : '', href: el && el.href ? el.href.slice(0,160) : '',
      selector: selectorFor(el),
      rect: {x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height)}
    });
  }, true);
  return 'a11y evidence tab listener injected';
})()'''


CHECK_TAB_STATUS_JS = '''(() => {
  const el = document.activeElement;
  const data = window.__a11yEvidenceTabData ? window.__a11yEvidenceTabData : [];
  const isBody = !el || el === document.body || el === document.documentElement;
  const isBack = Boolean(window.__a11yEvidenceFirstFocused && el === window.__a11yEvidenceFirstFocused && data.length > 1);
  return {isBody, isBack, count: data.length, currentTag: el ? el.tagName : 'null', currentId: el ? (el.id || '') : ''};
})()'''


GET_TAB_DATA_JS = '''() => window.__a11yEvidenceTabData || []'''


GET_INTERACTIVE_CANDIDATES_JS = '''(() => {
  const selectors = `a[href], button, input:not([type='hidden']), select, textarea, [tabindex]:not([tabindex='-1']), [role='button'], [role='link'], [role='menuitem'], [role='tab'], [contenteditable='true'], [onclick], [data-action], .action-menu-item, .ui-datepicker-prev, .ui-datepicker-next, .pika-prev, .pika-next, tr[title]`;
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
  function pointerEvidenceFor(el) {
    const evidence = [];
    if (el.matches("a[href], button, input:not([type='hidden']), select, textarea")) evidence.push('native-control');
    if (el.matches("[tabindex]:not([tabindex='-1'])")) evidence.push('positive-tabstop');
    if (el.matches("[tabindex='-1']")) evidence.push('tabindex-minus-one');
    if (el.matches("[role='button'], [role='link'], [role='menuitem'], [role='tab']")) evidence.push('aria-widget-role');
    if (el.matches('[onclick]')) evidence.push('onclick');
    if (el.matches('[data-action]')) evidence.push('data-action');
    if (el.matches('.action-menu-item')) evidence.push('action-menu-item');
    if (el.matches('.ui-datepicker-prev, .ui-datepicker-next, .pika-prev, .pika-next')) evidence.push('datepicker-month-control');
    if (looksLikePointerOperableRow(el)) evidence.push('pointer-operable-row');
    return evidence;
  }
  function looksLikePointerOperableRow(el) {
    if (!el || !el.matches('tr[title]')) return false;
    const table = el.closest('table');
    if (!table) return false;
    const contextText = [table.id, table.className, table.getAttribute('role'), table.closest('[class*="grid"], [id*="Grid"], [id*="grid"]')?.className || ''].join(' ').toLowerCase();
    const rowText = [el.id, el.className, el.getAttribute('data-bind'), el.getAttribute('data-role'), el.getAttribute('onclick'), el.getAttribute('title')].join(' ').toLowerCase();
    const gridContext = contextText.includes('grid') || contextText.includes('data-grid') || table.querySelector('thead') !== null;
    const pointerCue = el.hasAttribute('title') || rowText.includes('click') || rowText.includes('href') || rowText.includes('data-row') || window.getComputedStyle(el).cursor === 'pointer';
    return gridContext && pointerCue;
  }
  const uniqueCandidates = [];
  Array.from(document.querySelectorAll(selectors)).forEach((el) => {
    if (el.matches('tr[title]') && !looksLikePointerOperableRow(el)) return;
    if (uniqueCandidates.indexOf(el) === -1) uniqueCandidates.push(el);
  });
  return uniqueCandidates.filter(visible).map((el, index) => {
    const r = el.getBoundingClientRect();
    return {index: index + 1, tag: el.tagName || '', id: el.id || '', role: el.getAttribute('role') || '', text: (el.textContent || '').trim().slice(0,80), ariaLabel: el.getAttribute('aria-label') || '', title: el.getAttribute('title') || '', href: (el.href || '').slice(0,160), className: (el.className || '').toString().slice(0,120), tabIndex: el.getAttribute('tabindex') || '', pointerEvidence: pointerEvidenceFor(el), selector: selectorFor(el), rect: {x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height)}};
  });
})()'''


SCAN_COMPOSITE_WIDGETS_JS = '''(() => {
  // SCAN_A11Y_COMPOSITE_WIDGETS
  const selectors = `[role='menu'], [role='menubar'], [role='tablist'], [role='listbox'], [role='radiogroup'], [role='tree'], [role='toolbar']`;
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
  function info(el) {
    const r = el.getBoundingClientRect();
    return {tag: el.tagName || '', id: el.id || '', role: el.getAttribute('role') || '', text: (el.textContent || '').trim().slice(0,80), ariaLabel: el.getAttribute('aria-label') || '', title: el.getAttribute('title') || '', href: (el.href || '').slice(0,160), selector: selectorFor(el), rect: {x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height)}};
  }
  return Array.from(document.querySelectorAll(selectors)).filter(visible).map((container) => {
    const children = Array.from(container.querySelectorAll(`[role='menuitem'], [role='menuitemcheckbox'], [role='menuitemradio'], [role='tab'], [role='option'], [role='radio'], [role='treeitem'], button, a[href]`)).filter(visible).map(info);
    return {containerRole: container.getAttribute('role') || '', children};
  }).filter((container) => container.children.length > 0);
})()'''


CHECK_ACTIVE_ELEMENT_JS = '''(() => {
  // CHECK_A11Y_ACTIVE_ELEMENT
  let el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return {tag: 'BODY', id: '', role: '', text: '', ariaLabel: '', title: '', href: '', rect: null};
  const activeId = el.getAttribute ? el.getAttribute('aria-activedescendant') : '';
  if (activeId && document.getElementById(activeId)) el = document.getElementById(activeId);
  const r = el.getBoundingClientRect();
  function selectorFor(node) {
    if (!node || !node.tagName) return '';
    if (node.id) return '#' + CSS.escape(node.id);
    const parts = [];
    while (node && node !== document.body && node !== document.documentElement) {
      let part = node.tagName.toLowerCase();
      const parent = node.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((sibling) => sibling.tagName === node.tagName);
        if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(node) + 1) + ')';
      }
      parts.unshift(part);
      node = parent;
    }
    return parts.join(' > ');
  }
  const selector = selectorFor(el);
  return {tag: el.tagName || '', id: el.id || '', role: el.getAttribute('role') || '', text: (el.textContent || '').trim().slice(0,80), ariaLabel: el.getAttribute('aria-label') || '', title: el.getAttribute('title') || '', href: (el.href || '').slice(0,160), selector: selector, rect: {x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY), w: Math.round(r.width), h: Math.round(r.height)}};
})()'''


def _with_keyboard_marker_ids(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    marked: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        item.setdefault('marker_id', f'A11Y-K{index}')
        item.setdefault('label', item.get('ariaLabel') or item.get('text') or item.get('id') or item.get('role') or '')
        marked.append(item)
    return marked


def _simple_element_key(item: dict[str, Any]) -> str:
    return '|'.join(str(item.get(key) or '').strip().lower() for key in ('tag', 'id', 'role', 'text', 'ariaLabel', 'href'))


def _with_inventory_source(candidates: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    marked: list[dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        item['inventorySource'] = source
        marked.append(item)
    return marked


def _candidate_identity(item: dict[str, Any]) -> str:
    selector = str(item.get('selector') or '').strip()
    if selector:
        return f'selector:{selector}'
    rect = item.get('rect') if isinstance(item.get('rect'), dict) else {}
    return '|'.join([
        str(item.get('tag') or '').strip().lower(),
        str(item.get('text') or '').strip().lower(),
        str(item.get('title') or '').strip().lower(),
        str(rect.get('x') or ''),
        str(rect.get('y') or ''),
        str(rect.get('w') or ''),
        str(rect.get('h') or ''),
    ])


def _is_transient_widget_candidate(item: dict[str, Any]) -> bool:
    evidence = {str(entry).strip().lower() for entry in (item.get('pointerEvidence') or [])}
    if evidence & {'datepicker-month-control', 'action-menu-item'}:
        return True
    text = ' '.join(str(item.get(key) or '').lower() for key in ('selector', 'className'))
    return 'ui-datepicker-prev' in text or 'ui-datepicker-next' in text or 'action-menu-item' in text


def _merge_keyboard_inventories(
    pre_tab_candidates: list[dict[str, Any]],
    post_tab_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = _with_inventory_source(post_tab_candidates, 'post_tab')
    seen = {_candidate_identity(item) for item in merged}
    for candidate in pre_tab_candidates:
        if not _is_transient_widget_candidate(candidate):
            continue
        identity = _candidate_identity(candidate)
        if identity in seen:
            continue
        item = dict(candidate)
        item['inventorySource'] = 'pre_tab_transient_widget'
        merged.append(item)
        seen.add(identity)
    for index, item in enumerate(merged, start=1):
        item['index'] = index
    return merged


async def collect_composite_arrow_data(page: Any, *, arrow_interval_ms: int = 100) -> dict[str, Any]:
    containers = await page.evaluate(SCAN_COMPOSITE_WIDGETS_JS) or []
    result_containers: list[dict[str, Any]] = []
    for container in containers:
        children = container.get('children') or []
        reached: list[dict[str, Any]] = []
        for key in ('ArrowRight', 'ArrowDown'):
            await page.keyboard.press(key)
            if arrow_interval_ms > 0:
                await page.wait_for_timeout(arrow_interval_ms)
            active = await page.evaluate(CHECK_ACTIVE_ELEMENT_JS)
            if active and active.get('tag') != 'BODY':
                reached.append(active)
        reached_keys = {_simple_element_key(item) for item in reached}
        unreachable = [child for child in children if _simple_element_key(child) not in reached_keys]
        result_containers.append({
            'containerRole': container.get('containerRole') or container.get('role') or '',
            'children': children,
            'reachedSequence': reached,
            'unreachable': unreachable,
        })
    return {'containers': result_containers}


async def collect_keyboard_reachability_candidates(
    page: Any,
    *,
    target_description: str = '',
    max_tabs: int = 300,
    tab_interval_ms: int = 200,
    arrow_data: dict[str, Any] | None = None,
    collect_arrow: bool = False,
    arrow_interval_ms: int = 100,
) -> dict[str, Any]:
    await page.evaluate(INJECT_TAB_LISTENER_JS)
    pre_tab_interactive_candidates = _with_inventory_source(
        await page.evaluate(GET_INTERACTIVE_CANDIDATES_JS) or [],
        'pre_tab',
    )
    stop_reason = 'max_tabs_reached'
    consecutive_body = 0
    tab_press_count = 0

    for tab_press_count in range(1, max_tabs + 1):
        await page.keyboard.press('Tab')
        if tab_interval_ms > 0:
            await page.wait_for_timeout(tab_interval_ms)
        status = await page.evaluate(CHECK_TAB_STATUS_JS)
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

    tab_trace = await page.evaluate(GET_TAB_DATA_JS) or []
    post_tab_interactive_candidates = _with_inventory_source(
        await page.evaluate(GET_INTERACTIVE_CANDIDATES_JS) or [],
        'post_tab',
    )
    interactive_candidates = _merge_keyboard_inventories(pre_tab_interactive_candidates, post_tab_interactive_candidates)
    if collect_arrow and arrow_data is None:
        arrow_data = await collect_composite_arrow_data(page, arrow_interval_ms=arrow_interval_ms)
    summary = summarize_keyboard_reachability(
        tab_trace,
        interactive_candidates,
        arrow_data=arrow_data,
        target_description=target_description,
    )
    suspect_candidates = _with_keyboard_marker_ids(
        select_keyboard_reachability_suspects(summary)
    )

    return {
        'family': 'keyboard_nonreachable',
        'collection_method': 'real_tab_trace_plus_interactive_inventory',
        'target_description': target_description,
        'stop_reason': stop_reason,
        'max_tabs': max_tabs,
        'tab_interval_ms': tab_interval_ms,
        'tab_presses': tab_press_count,
        'tab_trace': tab_trace,
        'pre_tab_interactive_candidates': pre_tab_interactive_candidates,
        'post_tab_interactive_candidates': post_tab_interactive_candidates,
        'interactive_candidates': interactive_candidates,
        'arrow_data': arrow_data,
        'summary': summary,
        'suspect_candidates': suspect_candidates,
    }
