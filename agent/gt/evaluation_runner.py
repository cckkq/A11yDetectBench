from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def build_task_output_dir_name(task_id: str) -> str:
    if sys.platform != 'win32':
        return task_id

    import hashlib

    parts = task_id.split('.')
    prefix = '.'.join(parts[:3]) if len(parts) >= 3 else task_id[:24]
    if len(prefix) > 40 and len(parts) >= 2:
        prefix = '.'.join(parts[:2])
    if len(prefix) > 40:
        prefix = prefix[:40]

    if task_id.endswith('.verify.level3.v1'):
        variant = 'verify_l3_v1'
    elif task_id.endswith('.verify.level2.v1'):
        variant = 'verify_l2_v1'
    elif task_id.endswith('.verify.v1'):
        variant = 'verify_v1'
    else:
        variant = '_'.join(parts[-3:]).replace('level', 'l')

    digest = hashlib.sha1(task_id.encode('utf-8')).hexdigest()[:8]
    return f'{prefix}.{variant}.{digest}'


def run_dir_for_task(runs_root: Path, task_id: str, run_id: str) -> Path:
    return runs_root / build_task_output_dir_name(task_id) / run_id


def task_id_for_run(run: dict[str, Any]) -> str:
    task_id = run.get('task_id')
    if task_id:
        return str(task_id)
    return f"{run['task_base']}.{run['task_variant']}"


def build_evaluate_command(domain_module: str, run_dir: Path, *, headless: bool, timeout_ms: int = 30000) -> list[str]:
    cmd = [
        sys.executable,
        '-m',
        f'agent.{domain_module}.evaluate_run',
        '--run-dir',
        str(run_dir),
        '--output',
        str(run_dir / 'evaluation.json'),
        '--timeout',
        str(timeout_ms),
    ]
    if not headless:
        cmd.append('--headed')
    return cmd


def _read_evaluation(evaluation_path: Path) -> dict[str, Any]:
    if not evaluation_path.exists():
        return {
            'evaluator_error': True,
            'error_type': 'missing_evaluation_json',
            'gold_resolution_errors': [],
            'overall_pass': False,
        }
    try:
        loaded = json.loads(evaluation_path.read_text(encoding='utf-8'))
    except Exception as exc:
        return {
            'evaluator_error': True,
            'error_type': 'invalid_evaluation_json',
            'error': str(exc),
            'gold_resolution_errors': [],
            'overall_pass': False,
        }
    if not isinstance(loaded, dict):
        return {
            'evaluator_error': True,
            'error_type': 'invalid_evaluation_shape',
            'gold_resolution_errors': [],
            'overall_pass': False,
        }
    return loaded


def _as_string(value: Any) -> str:
    return '' if value is None else str(value)


def _is_login_like_url(url: Any) -> bool:
    return bool(re.search(r'/auth/login/?|/customer/account/login/?|/login(\?|/|$)|/signin(\?|/|$)', _as_string(url), re.I))


def _looks_like_auth_failure(page: dict[str, Any]) -> bool:
    start_url = page.get('start_url')
    final_url = page.get('final_url')
    try:
        status = int(page.get('http_status'))
    except Exception:
        status = 0
    return (_is_login_like_url(final_url) and not _is_login_like_url(start_url)) or status >= 400


def summarize_evaluation_status(run_dir: Path, *, returncode: int) -> dict[str, Any]:
    evaluation = _read_evaluation(run_dir / 'evaluation.json')
    gold_resolution_errors = evaluation.get('gold_resolution_errors') if isinstance(evaluation.get('gold_resolution_errors'), list) else []
    selector_errors = evaluation.get('selector_errors') if isinstance(evaluation.get('selector_errors'), list) else []
    gold_selector_errors = [err for err in selector_errors if isinstance(err, dict) and _as_string(err.get('side')) == 'gold']
    missing_core_fields = [key for key in ('task_id', 'instance_id', 'expected_verdict') if not evaluation.get(key)]
    expected_verdict = _as_string(evaluation.get('expected_verdict'))
    page = evaluation.get('page') if isinstance(evaluation.get('page'), dict) else {}
    expected_issue_without_gold_selectors = (
        expected_verdict == 'issue_found'
        and isinstance(evaluation.get('gold_selectors'), list)
        and not evaluation.get('gold_selectors')
    )
    auth_or_http_for_issue_task = expected_verdict == 'issue_found' and _looks_like_auth_failure(page)

    unexpected_returncode = returncode not in {0, 1, 2}
    evaluator_error = (
        bool(evaluation.get('evaluator_error'))
        or returncode == 2
        or unexpected_returncode
        or bool(missing_core_fields)
        or bool(gold_resolution_errors)
        or bool(gold_selector_errors)
        or expected_issue_without_gold_selectors
        or auth_or_http_for_issue_task
    )
    error_type = evaluation.get('error_type')
    if missing_core_fields and not error_type:
        error_type = 'missing_core_evaluation_fields'
    elif gold_resolution_errors and not error_type:
        error_type = 'gold_resolution'
    elif gold_selector_errors and not error_type:
        error_type = 'gold_selector_error'
    elif expected_issue_without_gold_selectors and not error_type:
        error_type = 'expected_issue_without_gold_selectors'
    elif auth_or_http_for_issue_task and not error_type:
        error_type = 'auth_or_http_for_issue_task'
    elif unexpected_returncode and not error_type:
        error_type = 'unexpected_evaluator_returncode'
    if evaluator_error:
        status = 'evaluator_error'
    elif bool(evaluation.get('overall_pass')) and returncode == 0:
        status = 'evaluated_pass'
    else:
        status = 'evaluated_fail'

    return {
        'status': status,
        'evaluation_returncode': returncode,
        'evaluation_path': str(run_dir / 'evaluation.json'),
        'overall_pass': bool(evaluation.get('overall_pass')),
        'evaluator_error': evaluator_error,
        'error_type': error_type,
        'missing_core_fields': missing_core_fields,
        'gold_resolution_error_count': len(gold_resolution_errors),
        'selector_error_count': len(selector_errors),
        'gold_selector_error_count': len(gold_selector_errors),
        'task_id': evaluation.get('task_id'),
        'instance_id': evaluation.get('instance_id'),
        'expected_verdict': evaluation.get('expected_verdict'),
        'observed_verdict': evaluation.get('observed_verdict'),
    }
