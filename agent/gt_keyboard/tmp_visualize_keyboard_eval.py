'''Visual audit image generator for one Keyboard evaluation run.'''

from __future__ import annotations

import argparse
import asyncio
import base64
import html
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.gt.probe_auth import probe  # noqa: E402
from agent.gt.save_storage_state import create_storage_state  # noqa: E402
from agent.gt_keyboard.evaluate_run import (  # noqa: E402
    _normalize_issue_family,
    _wait_for_gold_selector_groups,
    gold_issues,
    gold_selector_groups,
    load_json,
    load_yaml,
    normalize_issues,
    selectors_for_gold_issue,
    start_url_from_snapshots,
    storage_state_from_run,
)

VIEWPORT = {'width': 1280, 'height': 900}
COLORS = {
    'gt_blue': '#2563eb',
    'agent_ok': '#16a34a',
    'agent_type': '#f59e0b',
    'agent_target': '#ef4444',
    'agent_extra': '#dc2626',
}


def _single_gold_issue(rule: dict[str, Any]) -> list[dict[str, Any]]:
    gold = rule.get('gold') if isinstance(rule.get('gold'), dict) else {}
    target = gold.get('target') if isinstance(gold.get('target'), dict) else {}
    if not target:
        return []
    return [{'issue_id': str(rule.get('instance_id') or 'gold'), 'target': target, 'criterion': gold.get('criterion') or {}}]


def _infer_site(task: dict[str, Any], rule: dict[str, Any]) -> str | None:
    page = rule.get('page') if isinstance(rule.get('page'), dict) else {}
    site = page.get('site') or task.get('site')
    if site:
        return str(site)
    for key in ('instance_id', 'task_id'):
        value = str(task.get(key) or rule.get(key) or '')
        if '.' in value:
            return value.split('.', 1)[0]
    return None


async def _refreshed_storage_state(run_dir: Path, task: dict[str, Any], rule: dict[str, Any]) -> Path:
    site = _infer_site(task, rule)
    if not site:
        raise ValueError('Cannot infer site for auth refresh')
    output = run_dir / 'visual_refreshed_auth.storage_state.json'
    await create_storage_state(site, output, headed=False)
    ok, reason = await probe(site, output)
    if not ok:
        raise RuntimeError(f'Visual auth refresh failed for {site}: {reason}')
    return output


def _gold_family(issue: dict[str, Any], rule: dict[str, Any]) -> str:
    criterion = issue.get('criterion') if isinstance(issue.get('criterion'), dict) else {}
    family = criterion.get('issue_family')
    if family:
        return str(family)
    gold = rule.get('gold') if isinstance(rule.get('gold'), dict) else {}
    criterion = gold.get('criterion') if isinstance(gold.get('criterion'), dict) else {}
    return str(criterion.get('issue_family') or 'unknown')


def _matched_agent_to_gold(evaluation: dict[str, Any]) -> dict[int, int]:
    out: dict[int, int] = {}
    for result in evaluation.get('gold_issue_results') or []:
        if not isinstance(result, dict):
            continue
        gi = result.get('gold_index')
        ai = result.get('matched_issue_index')
        if isinstance(gi, int) and isinstance(ai, int):
            out[ai] = gi
    if not out and isinstance(evaluation.get('matched_issue_index'), int):
        out[int(evaluation['matched_issue_index'])] = 0
    return out


def _candidate_index(evaluation: dict[str, Any]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for result in evaluation.get('gold_issue_results') or evaluation.get('issue_results') or []:
        if not isinstance(result, dict):
            continue
        if isinstance(result.get('index'), int):
            out.setdefault(result['index'], []).append(result)
        for cand in result.get('candidate_results') or []:
            if isinstance(cand, dict) and isinstance(cand.get('index'), int):
                out.setdefault(cand['index'], []).append(cand)
    return out


def _gold_match_by_index(evaluation: dict[str, Any]) -> dict[int, bool]:
    out: dict[int, bool] = {}
    for result in evaluation.get('gold_issue_results') or evaluation.get('issue_results') or []:
        if isinstance(result, dict) and isinstance(result.get('gold_index'), int):
            out[result['gold_index']] = bool(result.get('match'))
    if not out and isinstance(evaluation.get('matched_issue_index'), int):
        out[0] = True
    if not out and evaluation.get('expected_count') in (0, 1):
        out[0] = bool(evaluation.get('matched_count') == 1 or evaluation.get('matched_issue_index') is not None)
    return out


def _issue_present(rule: dict[str, Any]) -> bool:
    gold = rule.get('gold') if isinstance(rule.get('gold'), dict) else {}
    expected = str(gold.get('expected_verdict') or '').strip()
    return bool(gold.get('issue_present', expected == 'issue_found'))


def _gold_items(rule: dict[str, Any], evaluation: dict[str, Any]) -> list[dict[str, Any]]:
    issues = gold_issues(rule) or _single_gold_issue(rule)
    matched = _gold_match_by_index(evaluation)
    issue_present = _issue_present(rule)
    items: list[dict[str, Any]] = []
    for gi, issue in enumerate(issues):
        family = _gold_family(issue, rule)
        status = 'matched' if matched.get(gi) else 'missing'
        if not issue_present:
            status = 'clean_target'
        for si, selector in enumerate(selectors_for_gold_issue(issue)):
            items.append({
                'selector': selector,
                'label': f'GT#{gi}.{si} {family} {status}',
                'color': COLORS['gt_blue'],
                'style': 'solid',
            })
    return items


def _agent_status(agent_index: int, evaluation: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[str, str]:
    if agent_index in _matched_agent_to_gold(evaluation):
        return 'match', COLORS['agent_ok']
    if any(c.get('selector_match') and not c.get('issue_type_match') for c in candidates):
        return 'type_mismatch', COLORS['agent_type']
    if any(c.get('issue_type_match') and not c.get('selector_match') for c in candidates):
        return 'wrong_target', COLORS['agent_target']
    return 'extra', COLORS['agent_extra']


def _agent_status_for_rule(agent_index: int, rule: dict[str, Any], evaluation: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[str, str]:
    if not _issue_present(rule):
        if agent_index in _matched_agent_to_gold(evaluation):
            return 'false_alarm_on_clean_target', COLORS['agent_extra']
        return 'unrelated_report', COLORS['agent_extra']
    return _agent_status(agent_index, evaluation, candidates)


def _agent_items(response: dict[str, Any], rule: dict[str, Any], evaluation: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    candidates = _candidate_index(evaluation)
    matched = _matched_agent_to_gold(evaluation)
    for ai, issue in enumerate(normalize_issues(response, rule)):
        selector = str(issue.get('selector') or '').strip()
        if not selector:
            continue
        family = _normalize_issue_family(str(issue.get('issue_type') or ''))
        status, color = _agent_status_for_rule(ai, rule, evaluation, candidates.get(ai, []))
        suffix = f' -> GT#{matched[ai]}' if ai in matched else ''
        items.append({'selector': selector, 'label': f'A#{ai} {family} {status}{suffix}', 'color': color, 'style': 'solid'})
    return items


def _missing_items(rule: dict[str, Any], evaluation: dict[str, Any]) -> list[dict[str, Any]]:
    if not _issue_present(rule):
        return []
    out: list[dict[str, Any]] = []
    for item in _gold_items(rule, evaluation):
        if 'missing' in item['label']:
            copy = dict(item)
            copy['label'] = copy['label'].replace('GT#', 'MISS GT#', 1)
            copy['color'] = COLORS['agent_extra']
            copy['style'] = 'dashed'
            out.append(copy)
    return out


async def _selector_has_visible_box(page: Any, selector: str) -> bool:
    try:
        locator = page.locator(selector)
        count = await locator.count()
    except Exception:
        return False
    for index in range(min(count, 20)):
        try:
            box = await locator.nth(index).bounding_box(timeout=1000)
        except Exception:
            continue
        if box and float(box.get('width') or 0) > 0 and float(box.get('height') or 0) > 0:
            return True
    return False


async def _any_selector_group_visible(page: Any, selector_groups: list[list[str]]) -> bool:
    for group in selector_groups:
        for selector in group:
            if selector and await _selector_has_visible_box(page, selector):
                return True
    return False


async def _click_first_visible(page: Any, selectors: list[str], label: str) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for selector in selectors:
        try:
            locator = page.locator(selector)
            count = await locator.count()
        except Exception:
            continue
        for index in range(min(count, 10)):
            item = locator.nth(index)
            try:
                if not await item.is_visible(timeout=1000):
                    continue
                await item.scroll_into_view_if_needed(timeout=2000)
                await item.click(timeout=5000)
                await page.wait_for_timeout(800)
                actions.append({'type': 'click', 'selector': selector, 'reason': label})
                return actions
            except Exception as exc:
                actions.append({'type': 'visual_precondition_error', 'selector': selector, 'reason': str(exc)})
                return actions
    return actions


async def _focus_first_visible(page: Any, selectors: list[str], label: str) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for selector in selectors:
        try:
            locator = page.locator(selector)
            count = await locator.count()
        except Exception:
            continue
        for index in range(min(count, 10)):
            item = locator.nth(index)
            try:
                if not await item.is_visible(timeout=1000):
                    continue
                await item.scroll_into_view_if_needed(timeout=2000)
                await item.focus(timeout=5000)
                await page.wait_for_timeout(800)
                actions.append({'type': 'focus', 'selector': selector, 'reason': label})
                return actions
            except Exception as exc:
                actions.append({'type': 'visual_precondition_error', 'selector': selector, 'reason': str(exc)})
                return actions
    return actions


async def _apply_visual_page_preconditions(page: Any, task: dict[str, Any], selector_groups: list[list[str]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    if await _any_selector_group_visible(page, selector_groups):
        return actions
    iid = str(task.get('instance_id') or '')
    if iid == 'gitlab.gl15.datepicker_month_switch_not_keyboard_reachable':
        actions.extend(await _focus_first_visible(page, ['#personal_access_token_expires_at', 'input[name="personal_access_token[expires_at]"]'], 'open GitLab PAT datepicker'))
    elif iid == 'gitlab.gl79.modal_selector_options_not_keyboard_reachable':
        actions.extend(await _click_first_visible(page, ['button:has-text("Connect a cluster")', 'a:has-text("Connect a cluster")', '[data-testid="connect-cluster-button"]', '.js-connect-cluster'], 'open Connect a cluster modal'))
    elif iid == 'gitlab.gl82.datepicker_month_switch_not_keyboard_reachable':
        actions.extend(await _click_first_visible(page, ['button[aria-label*="date" i]', '.js-daterange-picker button', '.js-daterange-picker input'], 'open Value Stream datepicker'))
    elif iid in {'shopping_admin.pa04.grid_toolbar_expanded_menu_items_not_tabbable', 'shopping_admin.pa05.grid_toolbar_expanded_menu_items_not_tabbable'}:
        actions.extend(await _click_first_visible(page, ['.admin__data-grid-header button.action-select', '.admin__data-grid-header .action-select', 'button:has-text("Actions")'], 'open Magento grid Actions menu'))
    elif iid in {'shopping_admin.pa08.datepicker_month_switch_not_keyboard_reachable', 'shopping_admin.pa50.datepicker_month_switch_not_keyboard_reachable'}:
        actions.extend(await _click_first_visible(page, ['button.ui-datepicker-trigger', 'button[data-bind*="datepicker"]', 'input.hasDatepicker', 'input._has-datepicker'], 'open Magento Admin datepicker'))
    elif iid == 'shopping_admin.pa11.collapsible_panel_expanded_content_partially_not_tabbable':
        actions.extend(await _click_first_visible(page, ['[data-index="schedule-design-update"] .admin__collapsible-title', '#catalog_category_tabs_design_section .admin__collapsible-title', 'legend:has-text("Schedule Design Update")', 'span:has-text("Schedule Design Update")'], 'expand Schedule Design Update panel'))
        actions.extend(await _click_first_visible(page, ['[data-index="schedule-design-update"] button.ui-datepicker-trigger', '#catalog_category_tabs_design_section button.ui-datepicker-trigger', 'button.ui-datepicker-trigger', '[data-index="schedule-design-update"] input.hasDatepicker'], 'open Schedule Design Update datepicker'))
    return actions


async def _prepare_page(browser: Any, task: dict[str, Any], start_url: str, storage_state: Path | None, selector_groups: list[list[str]], timeout_ms: int) -> tuple[Any, Any, dict[str, Any]]:
    context_kwargs: dict[str, Any] = {'viewport': VIEWPORT}
    if storage_state is not None:
        context_kwargs['storage_state'] = str(storage_state)
    context = await browser.new_context(**context_kwargs)
    page = await context.new_page()
    response = await page.goto(start_url, wait_until='domcontentloaded', timeout=timeout_ms)
    try:
        await page.wait_for_load_state('networkidle', timeout=min(timeout_ms, 8000))
    except Exception:
        pass
    await _wait_for_gold_selector_groups(page, selector_groups, timeout_ms=min(timeout_ms, 8000))
    actions = await _apply_visual_page_preconditions(page, task, selector_groups)
    meta = {'final_url': page.url, 'http_status': response.status if response is not None else None, 'precondition_actions': actions}
    return context, page, meta


async def _locator_boxes(page: Any, items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    placed: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for item in items:
        selector = str(item.get('selector') or '')
        try:
            locator = page.locator(selector)
            count = await locator.count()
        except Exception as exc:
            unresolved.append({'selector': selector, 'label': item.get('label'), 'reason': str(exc)})
            continue
        if count == 0:
            unresolved.append({'selector': selector, 'label': item.get('label'), 'reason': 'no resolved element'})
            continue
        found = 0
        for index in range(min(count, 50)):
            loc = locator.nth(index)
            try:
                await loc.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass
            try:
                box = await loc.bounding_box(timeout=2000)
            except Exception as exc:
                unresolved.append({'selector': selector, 'label': item.get('label'), 'reason': str(exc)})
                continue
            if not box:
                continue
            scroll = await page.evaluate('({x: window.scrollX, y: window.scrollY})')
            placed.append({
                'selector': selector,
                'label': item.get('label'),
                'color': item.get('color'),
                'style': item.get('style'),
                'x': float(box['x']) + float(scroll.get('x') or 0),
                'y': float(box['y']) + float(scroll.get('y') or 0),
                'width': max(8.0, float(box['width'])),
                'height': max(8.0, float(box['height'])),
            })
            found += 1
        if found == 0:
            unresolved.append({'selector': selector, 'label': item.get('label'), 'reason': 'no visible bounding box'})
    return {'placed': placed, 'unresolved': unresolved}


async def _draw_locator_overlay(page: Any, items: list[dict[str, Any]], title: str) -> dict[str, Any]:
    overlay = await _locator_boxes(page, items)
    script = r'''
    ({placed, unresolved, title}) => {
      const old = document.getElementById('__gt_eval_visual_overlay');
      if (old) old.remove();
      const root = document.createElement('div');
      root.id = '__gt_eval_visual_overlay';
      root.style.cssText = 'position:absolute;left:0;top:0;z-index:2147483647;pointer-events:none;';
      document.documentElement.appendChild(root);
      const banner = document.createElement('div');
      banner.textContent = title;
      banner.style.cssText = 'position:fixed;left:10px;top:10px;padding:6px 8px;background:#111827;color:white;font:700 14px Arial;z-index:2147483647;border-radius:4px;';
      root.appendChild(banner);
      placed.forEach((item, serial) => {
        const box = document.createElement('div');
        box.style.position = 'absolute';
        box.style.left = item.x + 'px';
        box.style.top = item.y + 'px';
        box.style.width = item.width + 'px';
        box.style.height = item.height + 'px';
        box.style.border = '3px ' + (item.style || 'solid') + ' ' + (item.color || '#2563eb');
        box.style.boxSizing = 'border-box';
        box.style.borderRadius = '3px';
        const label = document.createElement('div');
        label.textContent = item.label || item.selector;
        label.style.cssText = 'position:absolute;left:-3px;top:' + (-24 - (serial % 3) * 18) + 'px;max-width:520px;padding:2px 5px;background:' + (item.color || '#2563eb') + ';color:white;font:700 12px Arial;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-radius:3px;';
        box.appendChild(label);
        root.appendChild(box);
      });
      if (unresolved.length) {
        const panel = document.createElement('div');
        panel.style.cssText = 'position:fixed;left:10px;top:44px;max-width:900px;padding:6px 8px;background:rgba(107,114,128,.94);color:white;font:12px Consolas;z-index:2147483647;border-radius:4px;white-space:pre-wrap;';
        panel.textContent = 'Unresolved selectors:\n' + unresolved.map(x => `${x.label}: ${x.selector} (${x.reason})`).join('\n');
        root.appendChild(panel);
      }
      return {placed, unresolved};
    }
    '''
    return await page.evaluate(script, {'placed': overlay['placed'], 'unresolved': overlay['unresolved'], 'title': title})


def _summary_lines(task: dict[str, Any], evaluation: dict[str, Any]) -> list[str]:
    element = evaluation.get('element_expanded') if isinstance(evaluation.get('element_expanded'), dict) else {}
    grecall = float(evaluation.get('recall') or 0)
    gprecision = float(evaluation.get('precision') or 0)
    erecall = float(element.get('recall') or 0)
    eprecision = float(element.get('precision') or 0)
    return [
        f"task_id: {task.get('task_id') or ''}",
        f"overall_pass: {evaluation.get('overall_pass')} | verdict: expected {evaluation.get('expected_verdict')} / observed {evaluation.get('observed_verdict')}",
        f"group: expected {evaluation.get('expected_count')} | reported {evaluation.get('reported_count')} raw {evaluation.get('raw_reported_count')} | matched {evaluation.get('matched_count')} | R {grecall:.2f} / P {gprecision:.2f}",
        f"element: expected {element.get('expected_elements')} | reported {element.get('reported_elements')} | matched {element.get('matched_elements')} | R {erecall:.2f} / P {eprecision:.2f}",
    ]


def _image_data_uri(path: Path) -> str:
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


async def _compose(browser: Any, left_png: Path, right_png: Path, output_png: Path, summary: list[str]) -> None:
    page = await browser.new_page(viewport={'width': 2700, 'height': 1400})
    summary_html = ''.join(f'<div>{html.escape(line)}</div>' for line in summary)
    left_src = _image_data_uri(left_png)
    right_src = _image_data_uri(right_png)
    content = f'''
    <!doctype html><meta charset='utf-8'>
    <style>
    body {{ margin:0; padding:18px; background:#f3f4f6; font-family:Arial,sans-serif; color:#111827; }}
    .summary {{ background:white; border:1px solid #d1d5db; border-radius:6px; padding:10px 12px; font:14px Consolas,monospace; line-height:1.45; margin-bottom:12px; }}
    .row {{ display:flex; gap:14px; align-items:flex-start; }}
    .panel {{ background:white; border:1px solid #d1d5db; border-radius:6px; overflow:hidden; }}
    h2 {{ margin:0; padding:8px 10px; font-size:16px; background:#111827; color:white; }}
    img {{ display:block; width:1280px; height:auto; }}
    </style>
    <div class='summary'>{summary_html}<div>green=match, yellow=selector hit/type mismatch, red=wrong target/extra/missing, gray panel=unresolved selector</div></div>
    <div class='row'>
      <div class='panel'><h2>GT targets</h2><img src='{left_src}'></div>
      <div class='panel'><h2>Agent reported targets</h2><img src='{right_src}'></div>
    </div>
    '''
    await page.set_content(content, wait_until='load')
    await page.screenshot(path=str(output_png), full_page=True)
    await page.close()


async def visualize_run_dir(run_dir: Path, output: Path | None = None, timeout_ms: int = 30000, refresh_auth: bool = False) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    task_path = run_dir / 'task.snapshot.yaml'
    rule_path = run_dir / 'evaluate-rule.snapshot.yaml'
    response_path = run_dir / 'final-response.json'
    eval_path = run_dir / 'evaluation.json'
    meta_path = run_dir / 'meta.json'
    for required in (task_path, rule_path, response_path, eval_path):
        if not required.exists():
            raise FileNotFoundError(f'Required artifact not found: {required}')

    task = load_yaml(task_path)
    rule = load_yaml(rule_path)
    response = load_json(response_path)
    evaluation = load_json(eval_path)
    meta = load_json(meta_path) if meta_path.exists() else {}
    start_url = start_url_from_snapshots(task, rule)
    storage_state = await _refreshed_storage_state(run_dir, task, rule) if refresh_auth else storage_state_from_run(run_dir, task, meta, None)
    selector_groups = gold_selector_groups(rule)
    output_png = output or (run_dir / 'evaluation.visual.png')
    left_png = run_dir / 'evaluation.visual.gt.png'
    right_png = run_dir / 'evaluation.visual.agent.png'
    gt_items = _gold_items(rule, evaluation)
    right_items = _agent_items(response, rule, evaluation) + _missing_items(rule, evaluation)
    summary = _summary_lines(task, evaluation)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            left_context, left_page, left_page_meta = await _prepare_page(browser, task, start_url, storage_state, selector_groups, timeout_ms)
            left_overlay = await _draw_locator_overlay(left_page, gt_items, 'GT targets')
            await left_page.screenshot(path=str(left_png), full_page=True)
            await left_context.close()

            right_context, right_page, right_page_meta = await _prepare_page(browser, task, start_url, storage_state, selector_groups, timeout_ms)
            right_overlay = await _draw_locator_overlay(right_page, right_items, 'Agent reported targets')
            await right_page.screenshot(path=str(right_png), full_page=True)
            await right_context.close()

            await _compose(browser, left_png, right_png, output_png, summary)
        finally:
            await browser.close()

    payload = {
        'run_dir': str(run_dir),
        'output_png': str(output_png),
        'gt_side_png': str(left_png),
        'agent_side_png': str(right_png),
        'start_url': start_url,
        'storage_state_file': str(storage_state) if storage_state else None,
        'summary': summary,
        'gt_items': gt_items,
        'agent_items': right_items,
        'left_page': left_page_meta,
        'right_page': right_page_meta,
        'left_overlay': left_overlay,
        'right_overlay': right_overlay,
    }
    output_png.with_suffix('.meta.json').write_text(json.dumps(payload, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Visualize one Keyboard evaluation run.')
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timeout', type=int, default=30000)
    parser.add_argument('--refresh-auth', action='store_true')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = asyncio.run(visualize_run_dir(args.run_dir, args.output, args.timeout, args.refresh_auth))
    print(json.dumps({'output_png': payload['output_png']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
