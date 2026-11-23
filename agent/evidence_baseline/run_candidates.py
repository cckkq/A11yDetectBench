from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError('PyYAML is required to load candidate task/rule files.') from exc

from agent.evidence_baseline.focus_collector import collect_focus_visible_candidates
from agent.evidence_baseline.keyboard_collector import collect_keyboard_reachability_candidates
from agent.evidence_baseline.offline_eval import evaluate_candidate_manifest_with_resolved_selectors


PROJECT_ROOT = Path(__file__).resolve().parents[2]
Collector = Callable[..., Awaitable[dict[str, Any]]]
Evaluator = Callable[..., Awaitable[dict[str, Any]]]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open('r', encoding='utf-8') as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f'YAML root must be a mapping: {path}')
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)
        handle.write('\n')


def resolve_path(path_text: str | None, base: Path = PROJECT_ROOT) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    return path if path.is_absolute() else base / path


def infer_candidate_family(task: dict[str, Any], rule: dict[str, Any] | None = None) -> str:
    values = [task.get('issue_family'), task.get('issue_domain'), task.get('wcag_target')]
    if rule:
        criterion = ((rule.get('gold') or {}).get('criterion') or {})
        values.extend([rule.get('issue_family'), criterion.get('issue_family'), criterion.get('wcag_target')])
    text = ' '.join(str(value or '').lower().replace('_', ' ') for value in values)
    if 'visible focus' in text or 'focus visible' in text or '2.4.7' in text:
        return 'visible_focus'
    if 'keyboard nonreachable' in text or 'keyboard' in text or '2.1.1' in text:
        return 'keyboard_nonreachable'
    task_label = task.get('task_id') or task.get('instance_id')
    raise ValueError(f'Cannot infer evidence candidate family from task: {task_label}')


def target_description_from_task(task: dict[str, Any]) -> str:
    for key in ('target_description', 'scope', 'page_name'):
        value = task.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


def _suspect_manifest(full_manifest: dict[str, Any]) -> dict[str, Any]:
    keys = [
        'task_id', 'instance_id', 'family', 'collection_method', 'target_description',
        'stop_reason', 'max_tabs', 'tab_presses', 'suspect_candidates',
    ]
    return {key: full_manifest.get(key) for key in keys if key in full_manifest}


def _selector_lists_for_rule(family: str, rule: dict[str, Any]) -> tuple[list[str], list[list[str]]]:
    def split_selector_list(selector: str) -> list[str]:
        return [part.strip() for part in str(selector or '').split(',') if part.strip()]

    def expand_selectors(selectors: list[str]) -> list[str]:
        expanded: list[str] = []
        for selector in selectors:
            expanded.extend(split_selector_list(selector))
        return expanded

    def expand_groups(groups: list[list[str]]) -> list[list[str]]:
        return [expanded for group in groups if (expanded := expand_selectors(group))]

    if family == 'visible_focus':
        from agent.gt_focus import evaluate_run as focus_eval

        return expand_selectors(focus_eval.gold_selectors(rule)), expand_groups(focus_eval.gold_selector_groups(rule))
    if family == 'keyboard_nonreachable':
        from agent.gt_keyboard import evaluate_run as keyboard_eval

        return expand_selectors(keyboard_eval.gold_selectors(rule)), expand_groups(keyboard_eval.gold_selector_groups(rule))
    return [], []


def _resolver_for_family(family: str) -> Any:
    if family == 'visible_focus':
        from agent.gt_focus import evaluate_run as focus_eval

        return focus_eval.resolve_selectors_on_page
    if family == 'keyboard_nonreachable':
        from agent.gt_keyboard import evaluate_run as keyboard_eval

        return keyboard_eval.resolve_selectors_on_page
    raise ValueError(f'Unsupported candidate family: {family}')


def _evaluation_module_for_family(family: str) -> Any:
    if family == 'visible_focus':
        from agent.gt_focus import evaluate_run as focus_eval

        return focus_eval
    if family == 'keyboard_nonreachable':
        from agent.gt_keyboard import evaluate_run as keyboard_eval

        return keyboard_eval
    raise ValueError(f'Unsupported candidate family: {family}')


async def prepare_page_for_candidate_collection(
    *,
    page: Any,
    task: dict[str, Any],
    rule: dict[str, Any] | None,
    family: str,
    timeout_ms: int,
    eval_module: Any | None = None,
) -> dict[str, Any]:
    if rule is None:
        return {'attempted': False, 'actions': [], 'reason': 'no_evaluate_rule'}
    module = eval_module or _evaluation_module_for_family(family)
    _, selector_groups = _selector_lists_for_rule(family, rule)
    if not selector_groups:
        return {'attempted': False, 'actions': [], 'reason': 'no_gold_selector_groups'}

    await module._wait_for_gold_selector_groups(page, selector_groups, timeout_ms=min(timeout_ms, 8000))
    actions = await module._apply_known_page_preconditions(page, task or {}, rule or {}, selector_groups, timeout_ms)
    return {
        'attempted': True,
        'actions': actions,
        'selector_group_count': len(selector_groups),
    }


def _auth_provider_for_family(family: str) -> Any:
    if family == 'visible_focus':
        from agent.gt_focus import evaluate_run as focus_eval

        return focus_eval.storage_state_for_evaluation
    if family == 'keyboard_nonreachable':
        from agent.gt_keyboard import evaluate_run as keyboard_eval

        return keyboard_eval.storage_state_for_evaluation
    raise ValueError(f'Unsupported candidate family: {family}')


def _is_generated_pass_task(task_path: Path, task: dict[str, Any]) -> bool:
    joined = '/'.join(part.lower() for part in task_path.parts)
    if 'generated_pass' in joined:
        return True
    evaluate_rule_file = str(task.get('evaluate_rule_file') or '').lower()
    return 'generated_pass' in evaluate_rule_file


def _task_config_from_mapping(task_config_cls: Any, task: dict[str, Any]) -> Any:
    if not is_dataclass(task_config_cls):
        return task_config_cls.from_mapping(task)
    field_names = {field.name for field in fields(task_config_cls)}
    return task_config_cls.from_mapping({key: value for key, value in task.items() if key in field_names})


def runtime_patch_for_task(task_path: Path, task: dict[str, Any], family: str) -> dict[str, Any] | None:
    if not _is_generated_pass_task(task_path, task):
        return None
    if family == 'visible_focus':
        from agent.gt_focus import run_task as focus_run

        task_config = _task_config_from_mapping(focus_run.TaskConfig, task)
        patch_spec = focus_run.pass_l1_patch_for_task(task_path, task_config)
        if patch_spec is None:
            return None
        return {
            'family': family,
            'kind': str(patch_spec.get('kind') or ''),
            'instance_id': task_config.instance_id,
            'script': focus_run.make_pass_l1_patch_script(task_config, patch_spec),
        }
    if family == 'keyboard_nonreachable':
        from agent.gt_keyboard import run_task as keyboard_run

        task_config = _task_config_from_mapping(keyboard_run.TaskConfig, task)
        patch_spec = keyboard_run.pass_l1_patch_for_task(task_path, task_config)
        if patch_spec is None:
            return None
        return {
            'family': family,
            'kind': str(patch_spec.get('kind') or ''),
            'instance_id': task_config.instance_id,
            'script': keyboard_run.make_pass_l1_patch_script(task_config, patch_spec),
        }
    raise ValueError(f'Unsupported candidate family: {family}')


async def apply_runtime_patch_to_context(context: Any, runtime_patch: dict[str, Any] | None) -> bool:
    if not runtime_patch:
        return False
    script = str(runtime_patch.get('script') or '')
    if not script:
        return False
    await context.add_init_script(script)
    return True


def runtime_patch_metadata(runtime_patch: dict[str, Any] | None, *, applied: bool) -> dict[str, Any]:
    if not runtime_patch:
        return {'applied': False}
    return {
        'applied': applied,
        'family': runtime_patch.get('family'),
        'kind': runtime_patch.get('kind'),
        'instance_id': runtime_patch.get('instance_id'),
    }


async def prepare_storage_state(
    *,
    output_dir: Path,
    task: dict[str, Any],
    rule: dict[str, Any] | None,
    family: str,
    auth_state_file: str | None,
    headless: bool,
    provider: Any | None = None,
) -> tuple[Path | None, dict[str, Any]]:
    if rule is not None:
        auth_provider = provider or _auth_provider_for_family(family)
        return await auth_provider(
            run_dir=output_dir,
            task=task,
            rule=rule,
            meta={},
            override=auth_state_file,
            headless=headless,
        )

    storage_state_path = resolve_path(auth_state_file) or resolve_path(task.get('auth_state_file'))
    if storage_state_path is not None and not storage_state_path.exists():
        raise FileNotFoundError(f'Playwright storage state not found: {storage_state_path}')
    return storage_state_path, {
        'mode': 'direct',
        'storage_state_file': str(storage_state_path) if storage_state_path else None,
        'probe_ok': None,
        'probe_reason': None,
    }


async def evaluate_candidates_with_existing_resolver(
    *,
    manifest: dict[str, Any],
    task: dict[str, Any],
    rule: dict[str, Any],
    family: str,
    storage_state_path: Path | None,
    headless: bool,
    timeout_ms: int,
    runtime_patch: dict[str, Any] | None = None,
) -> dict[str, Any]:
    page_snapshot = rule.get('page') if isinstance(rule.get('page'), dict) else {}
    start_url = str(page_snapshot.get('start_url') or task.get('start_url') or '')
    if not start_url:
        raise ValueError('No start_url found in task or evaluate-rule snapshot')

    gold_selector_list, gold_selector_group_list = _selector_lists_for_rule(family, rule)
    candidate_selectors = [str(item.get('selector') or '').strip() for item in manifest.get('suspect_candidates') or []]
    candidate_selectors = [selector for selector in candidate_selectors if selector]
    page_result = await resolve_visible_selectors_on_fresh_page(
        start_url=start_url,
        gold_selector_list=gold_selector_list,
        gold_selector_group_list=gold_selector_group_list,
        agent_selector_list=candidate_selectors,
        storage_state_path=storage_state_path,
        headless=headless,
        timeout_ms=timeout_ms,
        task=task,
        rule=rule,
        family=family,
        runtime_patch=runtime_patch,
    )
    raw_resolutions = page_result.get('selector_resolutions') or {}
    selector_resolutions = {
        'gold': raw_resolutions.get('gold', {}),
        'candidate': raw_resolutions.get('candidate') or raw_resolutions.get('agent', {}),
        'relations': raw_resolutions.get('relations', {}),
    }
    result = evaluate_candidate_manifest_with_resolved_selectors(manifest, rule, selector_resolutions)
    result['page'] = {
        'start_url': page_result.get('start_url'),
        'final_url': page_result.get('final_url'),
        'http_status': page_result.get('http_status'),
        'precondition_actions': page_result.get('precondition_actions', []),
    }
    result['selector_errors'] = page_result.get('selector_errors', [])
    result['runtime_patch'] = page_result.get('runtime_patch', {'applied': False})
    return result


async def resolve_visible_selectors_on_fresh_page(
    *,
    start_url: str,
    gold_selector_list: list[str],
    gold_selector_group_list: list[list[str]],
    agent_selector_list: list[str],
    storage_state_path: Path | None,
    headless: bool,
    timeout_ms: int,
    task: dict[str, Any] | None,
    rule: dict[str, Any] | None,
    family: str,
    runtime_patch: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    eval_module = _evaluation_module_for_family(family)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            context_kwargs: dict[str, Any] = {'viewport': {'width': 1280, 'height': 900}}
            if storage_state_path is not None:
                context_kwargs['storage_state'] = str(storage_state_path)
            context = await browser.new_context(**context_kwargs)
            patch_applied = await apply_runtime_patch_to_context(context, runtime_patch)
            page = await context.new_page()
            response = await page.goto(start_url, wait_until='domcontentloaded', timeout=timeout_ms)
            try:
                await page.wait_for_load_state('networkidle', timeout=min(timeout_ms, 8000))
            except Exception:
                pass
            await eval_module._wait_for_gold_selector_groups(page, gold_selector_group_list, timeout_ms=min(timeout_ms, 8000))
            precondition_actions = await eval_module._apply_known_page_preconditions(page, task or {}, rule or {}, gold_selector_group_list, timeout_ms)
            resolved, errors = await resolve_visible_selectors_on_page(
                page=page,
                family=family,
                gold_selector_list=gold_selector_list,
                agent_selector_list=agent_selector_list,
            )
            return {
                'start_url': start_url,
                'final_url': page.url,
                'http_status': response.status if response is not None else None,
                'precondition_actions': precondition_actions,
                'selector_resolutions': resolved,
                'selector_errors': errors,
                'runtime_patch': runtime_patch_metadata(runtime_patch, applied=patch_applied),
            }
        finally:
            await browser.close()


async def resolve_selectors_on_page_with_runtime_patch(
    *,
    start_url: str,
    gold_selector_list: list[str],
    gold_selector_group_list: list[list[str]],
    agent_selector_list: list[str],
    storage_state_path: Path | None,
    headless: bool,
    timeout_ms: int,
    task: dict[str, Any] | None,
    rule: dict[str, Any] | None,
    family: str,
    runtime_patch: dict[str, Any] | None,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    eval_module = _evaluation_module_for_family(family)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            context_kwargs: dict[str, Any] = {'viewport': {'width': 1280, 'height': 900}}
            if storage_state_path is not None:
                context_kwargs['storage_state'] = str(storage_state_path)
            context = await browser.new_context(**context_kwargs)
            patch_applied = await apply_runtime_patch_to_context(context, runtime_patch)
            page = await context.new_page()
            response = await page.goto(start_url, wait_until='domcontentloaded', timeout=timeout_ms)
            try:
                await page.wait_for_load_state('networkidle', timeout=min(timeout_ms, 8000))
            except Exception:
                pass
            await eval_module._wait_for_gold_selector_groups(page, gold_selector_group_list, timeout_ms=min(timeout_ms, 8000))
            precondition_actions = await eval_module._apply_known_page_preconditions(page, task or {}, rule or {}, gold_selector_group_list, timeout_ms)
            seq_var = 'window.__gtFocusEvalSeq = 0' if family == 'visible_focus' else 'window.__gtKeyboardEvalSeq = 0'
            await page.evaluate(seq_var)

            resolved: dict[str, dict[str, list[str]]] = {'gold': {}, 'agent': {}}
            errors: list[dict[str, str]] = []
            for selector in gold_selector_list:
                ids, error = await eval_module._resolve_one_selector(page, selector)
                resolved['gold'][selector] = ids
                if error:
                    errors.append({'side': 'gold', 'selector': selector, 'error': error})
            for selector in agent_selector_list:
                ids, error = await eval_module._resolve_one_selector(page, selector)
                resolved['agent'][selector] = ids
                if error:
                    errors.append({'side': 'agent', 'selector': selector, 'error': error})

            return {
                'start_url': start_url,
                'final_url': page.url,
                'http_status': response.status if response is not None else None,
                'precondition_actions': precondition_actions,
                'selector_resolutions': resolved,
                'selector_errors': errors,
                'runtime_patch': runtime_patch_metadata(runtime_patch, applied=patch_applied),
            }
        finally:
            await browser.close()


async def resolve_visible_selectors_on_page(
    *,
    page: Any,
    family: str,
    gold_selector_list: list[str],
    agent_selector_list: list[str],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    id_property = '__a11yEvidenceFocusEvalId' if family == 'visible_focus' else '__a11yEvidenceKeyboardEvalId'
    prefix = 'evidence-focus' if family == 'visible_focus' else 'evidence-keyboard'

    async def resolve_one(selector: str) -> tuple[list[str], str | None]:
        if not selector:
            return [], 'empty selector'
        try:
            ids = await page.eval_on_selector_all(
                selector,
                """
                (elements, args) => {
                    const [idProperty, prefix] = args;
                    function visible(element) {
                        const rect = element.getBoundingClientRect();
                        const style = window.getComputedStyle(element);
                        return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
                    }
                    return elements.filter(element => {
                        return visible(element);
                    }).map(element => {
                        if (!element[idProperty]) {
                            const nextId = (window.__a11yEvidenceEvalSeq = (window.__a11yEvidenceEvalSeq || 0) + 1);
                            Object.defineProperty(element, idProperty, {
                                value: `${prefix}-${nextId}`,
                                configurable: true,
                            });
                        }
                        return element[idProperty];
                    });
                }
                """,
                [id_property, prefix],
            )
        except Exception as exc:
            return [], str(exc)
        return [str(item) for item in ids], None

    async def resolve_relation(agent_selector: str, gold_selector: str) -> tuple[list[dict[str, str]], str | None]:
        if not agent_selector or not gold_selector:
            return [], 'empty selector'
        try:
            relations = await page.evaluate(
                """
                (args) => {
                    const [agentSelector, goldSelector, idProperty, prefix] = args;
                    function visible(element) {
                        const rect = element.getBoundingClientRect();
                        const style = window.getComputedStyle(element);
                        return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
                    }
                    function ensureId(element) {
                        if (!element[idProperty]) {
                            const nextId = (window.__a11yEvidenceEvalSeq = (window.__a11yEvidenceEvalSeq || 0) + 1);
                            Object.defineProperty(element, idProperty, {
                                value: `${prefix}-${nextId}`,
                                configurable: true,
                            });
                        }
                        return element[idProperty];
                    }
                    const agents = Array.from(document.querySelectorAll(agentSelector)).filter(visible);
                    const golds = Array.from(document.querySelectorAll(goldSelector)).filter(visible);
                    const result = [];
                    for (const agent of agents) {
                        for (const gold of golds) {
                            let relation = '';
                            if (agent === gold) relation = 'exact';
                            else if (gold.contains(agent)) relation = 'candidate_descendant_of_gold';
                            else if (agent.contains(gold)) relation = 'candidate_ancestor_of_gold';
                            if (relation) {
                                result.push({
                                    relation,
                                    candidate_id: ensureId(agent),
                                    gold_id: ensureId(gold),
                                });
                            }
                        }
                    }
                    return result;
                }
                """,
                [agent_selector, gold_selector, id_property, prefix],
            )
        except Exception as exc:
            return [], str(exc)
        return [dict(item) for item in relations], None

    resolved: dict[str, Any] = {'gold': {}, 'agent': {}, 'relations': {'agent_to_gold': {}}}
    errors: list[dict[str, str]] = []
    for side, selectors in (('gold', gold_selector_list), ('agent', agent_selector_list)):
        for selector in selectors:
            ids, error = await resolve_one(selector)
            resolved[side][selector] = ids
            if error:
                errors.append({'side': side, 'selector': selector, 'error': error})
    for agent_selector in agent_selector_list:
        agent_relations: dict[str, list[dict[str, str]]] = {}
        for gold_selector in gold_selector_list:
            relations, error = await resolve_relation(agent_selector, gold_selector)
            agent_relations[gold_selector] = relations
            if error:
                errors.append({'side': 'relation', 'selector': agent_selector, 'gold_selector': gold_selector, 'error': error})
        resolved['relations']['agent_to_gold'][agent_selector] = agent_relations
    return resolved, errors


async def run_candidate_collection_on_page(
    *,
    page: Any,
    task: dict[str, Any],
    rule: dict[str, Any] | None,
    output_dir: Path,
    focus_collector: Collector = collect_focus_visible_candidates,
    keyboard_collector: Collector = collect_keyboard_reachability_candidates,
    evaluator: Evaluator | None = None,
    family: str | None = None,
    max_tabs: int = 300,
    tab_interval_ms: int = 200,
    collect_arrow: bool = True,
    focus_artifacts: bool = True,
    vlm_reviewer: Any = None,
    auth: dict[str, Any] | None = None,
    runtime_patch: dict[str, Any] | None = None,
    runtime_patch_applied: bool = False,
    page_setup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    family = family or infer_candidate_family(task, rule)
    target_description = target_description_from_task(task)

    if family == 'visible_focus':
        artifacts_dir = output_dir / 'focus-artifacts' if focus_artifacts else None
        manifest = await focus_collector(
            page,
            target_description=target_description,
            max_tabs=max_tabs,
            tab_interval_ms=tab_interval_ms,
            artifacts_dir=artifacts_dir,
            vlm_reviewer=vlm_reviewer,
        )
    elif family == 'keyboard_nonreachable':
        manifest = await keyboard_collector(
            page,
            target_description=target_description,
            max_tabs=max_tabs,
            tab_interval_ms=tab_interval_ms,
            collect_arrow=collect_arrow,
        )
    else:
        raise ValueError(f'Unsupported candidate family: {family}')

    manifest = dict(manifest)
    manifest.update({
        'task_id': task.get('task_id'),
        'instance_id': task.get('instance_id'),
        'family': family,
        'candidate_generation': {
            'uses_gold_rule': False,
            'uses_evaluate_rule': False,
            'uses_evaluate_rule_for_page_setup': bool(page_setup and page_setup.get('attempted')),
            'rule_used_only_for_offline_eval': bool(rule and evaluator),
            'page_setup': page_setup or {'attempted': False, 'actions': []},
        },
        'auth': auth or {},
        'runtime_patch': runtime_patch_metadata(runtime_patch, applied=runtime_patch_applied),
    })

    manifest_path = output_dir / 'candidate-manifest.full.json'
    suspect_manifest_path = output_dir / 'candidate-manifest.suspects.json'
    eval_path = output_dir / 'candidate-eval.json'
    write_json(manifest_path, manifest)
    write_json(suspect_manifest_path, _suspect_manifest(manifest))

    evaluation = None
    if rule is not None and evaluator is not None:
        evaluation = await evaluator(page=page, manifest=manifest, rule=rule, task=task)
        write_json(eval_path, evaluation)

    return {
        'manifest': manifest,
        'evaluation': evaluation,
        'manifest_path': manifest_path,
        'suspect_manifest_path': suspect_manifest_path,
        'evaluation_path': eval_path if evaluation is not None else None,
    }


def make_openai_focus_reviewer(model: str) -> Any:
    from agent.evidence_baseline.focus_vlm import make_default_focus_vlm_reviewer

    return make_default_focus_vlm_reviewer(model=model)


async def run_candidate_collection(
    *,
    task_path: Path,
    output_dir: Path,
    rule_path: Path | None = None,
    auth_state_file: str | None = None,
    headless: bool = True,
    timeout_ms: int = 30000,
    max_tabs: int = 300,
    tab_interval_ms: int = 200,
    collect_arrow: bool = True,
    focus_vlm_model: str | None = None,
) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    task = load_yaml(task_path)
    resolved_rule_path = rule_path or resolve_path(task.get('evaluate_rule_file'))
    rule = load_yaml(resolved_rule_path) if resolved_rule_path and resolved_rule_path.exists() else None
    family = infer_candidate_family(task, rule)
    page_snapshot = rule.get('page') if isinstance(rule, dict) and isinstance(rule.get('page'), dict) else {}
    start_url = str(page_snapshot.get('start_url') or task.get('start_url') or '')
    if not start_url:
        raise ValueError(f'No start_url found for task: {task_path}')
    runtime_patch = runtime_patch_for_task(task_path, task, family)

    storage_state_path, auth = await prepare_storage_state(
        output_dir=output_dir,
        task=task,
        rule=rule,
        family=family,
        auth_state_file=auth_state_file,
        headless=headless,
    )
    if auth.get('probe_ok') is False:
        reason = auth.get('probe_reason')
        raise RuntimeError(f'Auth probe failed before candidate collection: {reason}')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            context_kwargs: dict[str, Any] = {'viewport': {'width': 1280, 'height': 900}}
            if storage_state_path is not None:
                context_kwargs['storage_state'] = str(storage_state_path)
            context = await browser.new_context(**context_kwargs)
            patch_applied = await apply_runtime_patch_to_context(context, runtime_patch)
            page = await context.new_page()
            response = await page.goto(start_url, wait_until='domcontentloaded', timeout=timeout_ms)
            try:
                await page.wait_for_load_state('networkidle', timeout=min(timeout_ms, 8000))
            except Exception:
                pass

            page_setup = await prepare_page_for_candidate_collection(
                page=page,
                task=task,
                rule=rule,
                family=family,
                timeout_ms=timeout_ms,
            )

            async def default_evaluator(**kwargs: Any) -> dict[str, Any]:
                return await evaluate_candidates_with_existing_resolver(
                    manifest=kwargs['manifest'],
                    task=kwargs['task'],
                    rule=kwargs['rule'],
                    family=family,
                    storage_state_path=storage_state_path,
                    headless=headless,
                    timeout_ms=timeout_ms,
                    runtime_patch=runtime_patch,
                )

            result = await run_candidate_collection_on_page(
                page=page,
                task=task,
                rule=rule,
                output_dir=output_dir,
                evaluator=default_evaluator if rule is not None else None,
                family=family,
                max_tabs=max_tabs,
                tab_interval_ms=tab_interval_ms,
                collect_arrow=collect_arrow,
                vlm_reviewer=make_openai_focus_reviewer(focus_vlm_model) if focus_vlm_model and family == 'visible_focus' else None,
                auth=auth,
                runtime_patch=runtime_patch,
                runtime_patch_applied=patch_applied,
                page_setup=page_setup,
            )
            result['page'] = {
                'start_url': start_url,
                'final_url': page.url,
                'http_status': response.status if response is not None else None,
                'runtime_patch': runtime_patch_metadata(runtime_patch, applied=patch_applied),
                'candidate_collection_setup': page_setup,
            }
            return result
        finally:
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Collect first-stage accessibility evidence candidates for one task.')
    parser.add_argument('--task', required=True, type=Path, help='Task YAML path.')
    parser.add_argument('--rule', type=Path, help='Optional evaluate-rule YAML path. Defaults to task.evaluate_rule_file.')
    parser.add_argument('--output-dir', required=True, type=Path, help='Directory for candidate JSON artifacts.')
    parser.add_argument('--auth-state-file', help='Optional Playwright storage-state override.')
    parser.add_argument('--headed', action='store_true', help='Show the Playwright browser.')
    parser.add_argument('--timeout', type=int, default=30000, help='Navigation/selector timeout in milliseconds.')
    parser.add_argument('--max-tabs', type=int, default=300)
    parser.add_argument('--tab-interval-ms', type=int, default=200)
    parser.add_argument('--no-arrow', action='store_true', help='Disable keyboard composite arrow probing.')
    parser.add_argument('--focus-vlm-model', help='Optional local OpenAI-compatible VLM model for Focus crop review. Omit to use the non-VLM fallback collector.')
    parser.add_argument('--no-focus-vlm', action='store_true', help='Disable Focus VLM review explicitly.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = asyncio.run(run_candidate_collection(
        task_path=args.task,
        output_dir=args.output_dir,
        rule_path=args.rule,
        auth_state_file=args.auth_state_file,
        headless=not args.headed,
        timeout_ms=args.timeout,
        max_tabs=args.max_tabs,
        tab_interval_ms=args.tab_interval_ms,
        collect_arrow=not args.no_arrow,
        focus_vlm_model=None if args.no_focus_vlm else args.focus_vlm_model,
    ))
    print(json.dumps({
        'manifest_path': str(result['manifest_path']),
        'suspect_manifest_path': str(result['suspect_manifest_path']),
        'evaluation_path': str(result['evaluation_path']) if result['evaluation_path'] else None,
        'page': result.get('page'),
    }, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
