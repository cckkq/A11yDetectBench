#!/usr/bin/env python3
"""Parallel ERROR experiment entrypoint with strict ERROR output schema."""
from __future__ import annotations

import argparse
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from agent.gt.evaluation_runner import build_evaluate_command, run_dir_for_task, summarize_evaluation_status, task_id_for_run
from agent.gt_errors.experiment_manifest import expand_runs, load_experiment_manifest
from agent.gt_errors.parallel_runner import (
    append_status,
    assign_runs_to_workers,
    build_run_id,
    build_run_key,
    get_parallel_runs_root,
    get_runtime_attempt_root,
    get_worker_auth_state_path,
    get_worker_runtime_dir,
    load_completed_run_keys,
    parse_site_workers,
    plan_site_workers,
)


GT_ERRORS_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = GT_ERRORS_DIR / 'experiments' / 'formal_error_experiment_v1.yaml'
PRINT_LOCK = threading.Lock()
ANSI_RESET = '\x1b[0m'
SITE_COLORS = {
    'gitlab': '\x1b[36m',
    'reddit': '\x1b[35m',
    'shopping': '\x1b[32m',
    'shopping_admin': '\x1b[33m',
}
STATUS_COLORS = {
    'starting': '\x1b[34m',
    'running': '\x1b[37m',
    'refreshing': '\x1b[34m',
    'done': '\x1b[32m',
    'failed': '\x1b[31m',
    'evaluating': '\x1b[34m',
    'evaluated_pass': '\x1b[32m',
    'evaluated_fail': '\x1b[33m',
    'evaluator_error': '\x1b[31m',
    'auth_probe_failed': '\x1b[31m',
    'pre_task_reset_failed': '\x1b[31m',
    'skipped': '\x1b[33m',
    'idle': '\x1b[90m',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run a frozen ERROR GT experiment manifest in parallel with worker-private sessions.')
    parser.add_argument('--manifest', default=str(DEFAULT_MANIFEST), help='Path to experiment manifest YAML.')
    parser.add_argument('--list-only', action='store_true', help='List planned worker assignments without executing them.')
    parser.add_argument('--site', action='append', help='Limit to one or more sites.')
    parser.add_argument('--level', action='append', help='Limit to one or more task variants, e.g. verify.v1.')
    parser.add_argument('--repeat', type=int, action='append', help='Limit to one or more repeat indices.')
    parser.add_argument('--headless', action='store_true', help='Run task browsers headlessly.')
    parser.add_argument('--model', default='gpt-5.2-20251211', help='LLM model name for browser-use execution.')
    parser.add_argument('--reasoning-effort', help='Optional reasoning effort for LLM routes that support it, e.g. Copilot.')
    parser.add_argument('--parallel', type=int, default=6, help='Total worker count across all sites.')
    parser.add_argument('--refresh-session-every', type=int, default=1, help='Refresh worker auth session every N auth-required tasks (default 1 = every task).')
    parser.add_argument('--max-tasks-per-worker', type=int, help='Optional smoke cap for how many runs each worker may execute.')
    parser.add_argument('--site-workers', help='Optional explicit worker map, e.g. gitlab=2,shopping_admin=2,shopping=1,reddit=1')
    parser.add_argument('--resume', action='store_true', help='Skip runs already marked evaluated_pass/evaluated_fail in the current attempt status log.')
    parser.add_argument('--attempt-id', help='Optional explicit attempt id for runtime isolation.')
    parser.add_argument(
        '--prompt-footer-mode',
        choices=['full', 'omit-output-format'],
        default='full',
        help='Forwarded to run_task.py. Default full keeps the Output Format footer; omit-output-format removes it.',
    )
    parser.add_argument(
        '--disable-schema-enhancement',
        action='store_true',
        help='Forwarded to run_task.py. When set, monkey-patches browser-use to skip appending the output_model_schema JSON to each task prompt.',
    )
    parser.add_argument(
        '--capture-structured-failures',
        action='store_true',
        help='Forwarded to run_task.py. When set, full raw structured-output payloads on parse failures are dumped into the run directory.',
    )
    parser.add_argument(
        '--salvage-multi-json',
        action='store_true',
        help='Forwarded to run_task.py / create_llm. When set, ChatAzureOpenAI salvages the first valid JSON block when structured-output parsing fails and dumps dropped blocks for audit.',
    )
    parser.add_argument(
        '--reset-shopping-admin-grid-state',
        action='store_true',
        help='Before each shopping_admin run, clear Magento ui_bookmark rows to remove persisted admin grid/filter state. Requires shopping_admin=1.',
    )
    return parser.parse_args()


def filter_runs(runs: list[dict], args: argparse.Namespace) -> list[dict]:
    selected = runs
    if args.site:
        selected = [run for run in selected if run['site'] in set(args.site)]
    if args.level:
        selected = [run for run in selected if run['task_variant'] in set(args.level)]
    if args.repeat:
        selected = [run for run in selected if run['repeat_index'] in set(args.repeat)]
    return selected


def cap_worker_runs(workers: list[dict], max_tasks_per_worker: int | None) -> list[dict]:
    if max_tasks_per_worker is None:
        return workers
    capped: list[dict] = []
    for worker in workers:
        capped.append(
            {
                **worker,
                'runs': worker['runs'][:max_tasks_per_worker],
            }
        )
    return capped


def _status_key(status: str) -> str:
    if status.startswith('running'):
        return 'running'
    if status.startswith('refreshing'):
        return 'refreshing'
    if status.startswith('done'):
        return 'done'
    return status


def format_progress_snapshot(progress_by_worker: dict[int, dict]) -> str:
    parts: list[str] = []
    for worker_id in sorted(progress_by_worker):
        progress = progress_by_worker[worker_id]
        site = progress['site']
        status = progress['status']
        site_color = SITE_COLORS.get(site, '')
        status_color = STATUS_COLORS.get(_status_key(status), '')
        parts.append(
            f"{site_color}worker-{worker_id}[{site}]{ANSI_RESET} "
            f"{progress['done']}/{progress['total']} {status_color}{status}{ANSI_RESET}"
        )
    return ' | '.join(parts)


def should_echo_line(line: str) -> bool:
    lowered = line.lower().strip()
    noisy_substrings = [
        'http_logging_policy',
        'request url:',
        'request headers:',
        'response headers:',
        'content-length',
        'content-security-policy',
        'answer using the structured output fields only',
        'expected output format:',
        '"properties": {',
        '"required": [',
        'title":',
        'type": "string"',
        'target: string',
        'verdict: string',
        'issue_type: string',
        'observed_behavior: string',
        'evidence: string',
    ]
    if any(token in lowered for token in noisy_substrings):
        return False
    return True


def build_storage_state_command(site: str, output_path: str, headed_refresh: bool) -> list[str]:
    cmd = [
        sys.executable,
        '-m',
        'agent.gt.save_storage_state',
        site,
        '--output',
        output_path,
    ]
    if not headed_refresh:
        cmd.append('--headless')
    return cmd


def _print_progress(progress_by_worker: dict[int, dict]) -> None:
    with PRINT_LOCK:
        print(format_progress_snapshot(progress_by_worker), flush=True)


def _run_command_with_worker_log(cmd: list[str], worker_dir: Path, prefix: str) -> int:
    raw_log_path = worker_dir / 'worker.log'
    summary_log_path = worker_dir / 'worker.summary.log'
    worker_dir.mkdir(parents=True, exist_ok=True)
    with raw_log_path.open('a', encoding='utf-8') as raw_log, summary_log_path.open('a', encoding='utf-8') as summary_log:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            plain = f'[{prefix}] {line.rstrip()}'
            raw_log.write(plain + '\n')
            raw_log.flush()
            if should_echo_line(plain):
                summary_log.write(plain + '\n')
                summary_log.flush()
                with PRINT_LOCK:
                    print(plain, flush=True)
        return process.wait()


def _ensure_worker_auth_state(experiment_id: str, attempt_id: str, site: str, worker_id: int, batch_id: int, worker_dir: Path) -> Path:
    output_path = get_worker_auth_state_path(experiment_id, attempt_id, site, worker_id, batch_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = build_storage_state_command(site=site, output_path=str(output_path), headed_refresh=False)
    returncode = _run_command_with_worker_log(cmd, worker_dir, prefix=f'worker-{worker_id}:session')
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd)
    return output_path


def _probe_auth(site: str, storage_state_path: Path, worker_dir: Path, worker_id: int) -> tuple[bool, str]:
    """Run probe_auth as a subprocess. Returns (healthy, reason)."""
    cmd = [
        sys.executable,
        '-m',
        'agent.gt.probe_auth',
        site,
        '--storage-state',
        str(storage_state_path),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        return True, 'ok'
    reason = result.stderr.strip() or result.stdout.strip() or f'exit code {result.returncode}'
    # Log probe failure to worker log
    raw_log_path = worker_dir / 'worker.log'
    raw_log_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_log_path.open('a', encoding='utf-8') as f:
        f.write(f'[worker-{worker_id}:probe] probe FAILED for {site}: {reason}\n')
    return False, reason



def _reset_shopping_admin_grid_state(worker_dir: Path, worker_id: int) -> int:
    sql = 'DELETE FROM ui_bookmark;'
    cmd = [
        'docker',
        'exec',
        'shopping_admin',
        'mysql',
        '-u',
        'magentouser',
        '-pMyPassword',
        'magentodb',
        '-e',
        sql,
    ]
    return _run_command_with_worker_log(cmd, worker_dir, prefix=f'worker-{worker_id}:admin-reset')


def validate_reset_shopping_admin_grid_state_plan(reset_shopping_admin_grid_state: bool, site_workers: dict[str, int], runs: list[dict]) -> None:
    if not reset_shopping_admin_grid_state:
        return
    has_shopping_admin_runs = any(run['site'] == 'shopping_admin' for run in runs)
    if has_shopping_admin_runs and site_workers.get('shopping_admin') != 1:
        raise ValueError('--reset-shopping-admin-grid-state requires shopping_admin=1 to avoid cross-worker state deletion during active runs')

def _run_worker(
    experiment_id: str,
    attempt_id: str,
    worker: dict,
    refresh_session_every: int,
    headless: bool,
    status_path: Path,
    completed_keys: set[str],
    progress_by_worker: dict[int, dict],
    runs_root: Path,
    prompt_footer_mode: str = 'full',
    disable_schema_enhancement: bool = False,
    capture_structured_failures: bool = False,
    salvage_multi_json: bool = False,
    reset_shopping_admin_grid_state: bool = False,
    model: str = 'gpt-5.2-20251211',
    reasoning_effort: str | None = None,
) -> None:
    worker_id = worker['worker_id']
    site = worker['site']
    worker_dir = get_worker_runtime_dir(experiment_id, attempt_id, worker_id)
    worker_dir.mkdir(parents=True, exist_ok=True)
    batch_id = 0
    auth_tasks_since_refresh = 0
    auth_state_path: Path | None = None
    progress_by_worker[worker_id] = {
        'site': site,
        'done': 0,
        'total': len(worker['runs']),
        'status': 'starting',
    }
    _print_progress(progress_by_worker)

    if not worker['runs']:
        progress_by_worker[worker_id]['status'] = 'idle'
        _print_progress(progress_by_worker)
        return

    for queue_index, run in enumerate(worker['runs'], start=1):
        run_key = build_run_key(run)
        if run_key in completed_keys:
            append_status(
                status_path,
                {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'attempt_id': attempt_id,
                    'worker_id': worker_id,
                    'site': site,
                    'run_key': run_key,
                    'status': 'skipped_existing',
                },
            )
            progress_by_worker[worker_id]['done'] += 1
            progress_by_worker[worker_id]['status'] = 'skipped'
            _print_progress(progress_by_worker)
            continue

        auth_required = run.get('auth_required', True)

        # --- auth refresh logic (only for auth-required tasks) ---
        if auth_required:
            need_refresh = (
                auth_state_path is None  # first auth task
                or refresh_session_every == 1  # every auth task
                or (refresh_session_every > 1 and auth_tasks_since_refresh >= refresh_session_every)
            )
            if need_refresh:
                batch_id += 1
                auth_tasks_since_refresh = 0
                progress_by_worker[worker_id]['status'] = f'refreshing-batch-{batch_id}'
                _print_progress(progress_by_worker)
                auth_state_path = _ensure_worker_auth_state(
                    experiment_id,
                    attempt_id,
                    site,
                    worker_id,
                    batch_id,
                    worker_dir=worker_dir,
                )
            auth_tasks_since_refresh += 1

            # --- probe auth session ---
            probe_ok, probe_reason = _probe_auth(site, auth_state_path, worker_dir, worker_id)
            if not probe_ok:
                run_id = build_run_id(run, worker_id, queue_index=queue_index, batch_id=batch_id)
                append_status(
                    status_path,
                    {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'attempt_id': attempt_id,
                        'worker_id': worker_id,
                        'site': site,
                        'run_key': run_key,
                        'run_id': run_id,
                        'status': 'auth_probe_failed',
                        'session_batch_id': batch_id,
                        'probe_reason': probe_reason,
                    },
                )
                progress_by_worker[worker_id]['done'] += 1
                progress_by_worker[worker_id]['status'] = 'auth_probe_failed'
                _print_progress(progress_by_worker)
                continue

        run_id = build_run_id(run, worker_id, queue_index=queue_index, batch_id=batch_id)

        if reset_shopping_admin_grid_state and site == 'shopping_admin':
            progress_by_worker[worker_id]['status'] = 'resetting-admin-grid-state'
            _print_progress(progress_by_worker)
            reset_returncode = _reset_shopping_admin_grid_state(worker_dir=worker_dir, worker_id=worker_id)
            if reset_returncode != 0:
                append_status(
                    status_path,
                    {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'attempt_id': attempt_id,
                        'worker_id': worker_id,
                        'site': site,
                        'run_key': run_key,
                        'run_id': run_id,
                        'status': 'pre_task_reset_failed',
                        'session_batch_id': batch_id,
                        'queue_index': queue_index,
                        'returncode': reset_returncode,
                    },
                )
                progress_by_worker[worker_id]['done'] += 1
                progress_by_worker[worker_id]['status'] = 'pre_task_reset_failed'
                _print_progress(progress_by_worker)
                continue

        append_status(
            status_path,
            {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'attempt_id': attempt_id,
                'worker_id': worker_id,
                'site': site,
                'run_key': run_key,
                'run_id': run_id,
                'status': 'running',
                'session_batch_id': batch_id,
                'queue_index': queue_index,
            },
        )

        progress_by_worker[worker_id]['status'] = f"running:{run['instance_id']}"
        _print_progress(progress_by_worker)

        cmd = [
            sys.executable,
            '-m',
            'agent.gt_errors.run_task',
            '--task',
            run['task_path'],
            '--model',
            model,
            '--max-steps',
            str(run['max_steps']),
        ]
        if reasoning_effort:
            cmd.extend(['--reasoning-effort', reasoning_effort])
        if auth_required and auth_state_path is not None:
            cmd.extend(['--auth-state-file', str(auth_state_path)])
        cmd.extend([
            '--run-id',
            run_id,
            '--experiment-id',
            experiment_id,
            '--worker-id',
            str(worker_id),
            '--session-batch-id',
            str(batch_id),
            '--site',
            site,
            '--task-variant',
            run['task_variant'],
            '--repeat-index',
            str(run['repeat_index']),
            '--queue-index',
            str(queue_index),
            '--runs-root',
            str(runs_root),
        ])
        if headless:
            cmd.append('--headless')

        if prompt_footer_mode and prompt_footer_mode != 'full':
            cmd.extend(['--prompt-footer-mode', prompt_footer_mode])
        if disable_schema_enhancement:
            cmd.append('--disable-schema-enhancement')
        if capture_structured_failures:
            cmd.append('--capture-structured-failures')
        if salvage_multi_json:
            cmd.append('--salvage-multi-json')

        returncode = _run_command_with_worker_log(cmd, worker_dir, prefix=f'worker-{worker_id}:run')
        if returncode != 0:
            append_status(
                status_path,
                {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'attempt_id': attempt_id,
                    'worker_id': worker_id,
                    'site': site,
                    'run_key': run_key,
                    'run_id': run_id,
                    'status': 'failed',
                    'session_batch_id': batch_id,
                    'returncode': returncode,
                },
            )
            progress_by_worker[worker_id]['done'] += 1
            progress_by_worker[worker_id]['status'] = 'failed'
            _print_progress(progress_by_worker)
            continue

        run_dir = run_dir_for_task(runs_root, task_id_for_run(run), run_id)
        progress_by_worker[worker_id]['status'] = f"evaluating:{run['instance_id']}"
        _print_progress(progress_by_worker)
        eval_cmd = build_evaluate_command('gt_errors', run_dir, headless=headless)
        eval_returncode = _run_command_with_worker_log(eval_cmd, worker_dir, prefix=f'worker-{worker_id}:eval')
        evaluation_summary = summarize_evaluation_status(run_dir, returncode=eval_returncode)
        append_status(
            status_path,
            {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'attempt_id': attempt_id,
                'worker_id': worker_id,
                'site': site,
                'run_key': run_key,
                'run_id': run_id,
                'session_batch_id': batch_id,
                **evaluation_summary,
            },
        )
        progress_by_worker[worker_id]['done'] += 1
        progress_by_worker[worker_id]['status'] = evaluation_summary['status']
        _print_progress(progress_by_worker)

    progress_by_worker[worker_id]['status'] = 'done'
    _print_progress(progress_by_worker)


def print_worker_plan(experiment_id: str, attempt_id: str, workers: list[dict], refresh_session_every: int, max_tasks_per_worker: int | None, runs_root: Path) -> None:
    print(f'Experiment: {experiment_id}')
    print(f'Attempt: {attempt_id}')
    print(f'Parallel runs root: {runs_root}')
    print(
        f'Workers: {len(workers)} | refresh_session_every={refresh_session_every} '
        f"| max_tasks_per_worker={max_tasks_per_worker if max_tasks_per_worker is not None else 'all'}"
    )
    for worker in workers:
        print(f"- worker={worker['worker_id']} | site={worker['site']} | planned_runs={len(worker['runs'])}")
        for run in worker['runs']:
            print(
                f"  - {task_id_for_run(run)} | level={run['task_variant']} | repeat={run['repeat_index']} | "
                f"max_steps={run['max_steps']} | task_file={run['task_file']}"
            )


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    manifest = load_experiment_manifest(manifest_path)
    experiment_id = manifest.get('experiment_id', manifest_path.stem)
    attempt_id = args.attempt_id or datetime.now().strftime('attempt_%Y%m%d_%H%M%S')
    runs_root = get_parallel_runs_root(experiment_id, attempt_id=attempt_id)
    runs = filter_runs(expand_runs(manifest), args)

    explicit_site_workers = parse_site_workers(args.site_workers)
    if explicit_site_workers:
        site_workers = explicit_site_workers
    else:
        site_run_counts: dict[str, int] = {}
        for run in runs:
            site_run_counts[run['site']] = site_run_counts.get(run['site'], 0) + 1
        site_workers = plan_site_workers(site_run_counts, total_workers=args.parallel)

    validate_reset_shopping_admin_grid_state_plan(
        args.reset_shopping_admin_grid_state,
        site_workers=site_workers,
        runs=runs,
    )


    workers = assign_runs_to_workers(runs, site_workers=site_workers)
    workers = cap_worker_runs(workers, max_tasks_per_worker=args.max_tasks_per_worker)
    print_worker_plan(
        experiment_id,
        attempt_id,
        workers,
        refresh_session_every=args.refresh_session_every,
        max_tasks_per_worker=args.max_tasks_per_worker,
        runs_root=runs_root,
    )
    if args.list_only:
        return

    runs_root.mkdir(parents=True, exist_ok=True)
    runtime_attempt_root = get_runtime_attempt_root(experiment_id, attempt_id)
    runtime_attempt_root.mkdir(parents=True, exist_ok=True)
    status_path = runtime_attempt_root / 'plan_status.jsonl'
    completed_keys = load_completed_run_keys(status_path) if args.resume else set()
    progress_by_worker: dict[int, dict] = {}

    threads: list[threading.Thread] = []
    for worker in workers:
        thread = threading.Thread(
            target=_run_worker,
            kwargs={
                'experiment_id': experiment_id,
                'attempt_id': attempt_id,
                'worker': worker,
                'refresh_session_every': args.refresh_session_every,
                'headless': args.headless,
                'status_path': status_path,
                'completed_keys': completed_keys,
                'progress_by_worker': progress_by_worker,
                'runs_root': runs_root,
                'prompt_footer_mode': args.prompt_footer_mode,
                'disable_schema_enhancement': args.disable_schema_enhancement,
                'capture_structured_failures': args.capture_structured_failures,
                'salvage_multi_json': args.salvage_multi_json,
                'reset_shopping_admin_grid_state': args.reset_shopping_admin_grid_state,
                'model': args.model,
                'reasoning_effort': args.reasoning_effort,
            },
            daemon=False,
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    _print_progress(progress_by_worker)


if __name__ == '__main__':
    main()
