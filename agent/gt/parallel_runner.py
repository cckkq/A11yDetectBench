from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


GT_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = GT_DIR / 'runtime'
RUNTIME_AUTH_DIR = GT_DIR / 'auth' / 'runtime'
SERIAL_RUNS_DIR = GT_DIR / 'runs'
PARALLEL_RUNS_DIR = GT_DIR / 'runs_parallel'


def build_run_key(run: dict) -> str:
    task_id = run.get('task_id') or f"{run['instance_id']}.{run['task_variant']}"
    return f"{task_id}::repeat={run['repeat_index']}"


def plan_site_workers(site_run_counts: dict[str, int], total_workers: int) -> dict[str, int]:
    if total_workers <= 0:
        raise ValueError('total_workers must be positive')
    if not site_run_counts:
        return {}

    ordered_sites = sorted(site_run_counts.items(), key=lambda item: (-item[1], item[0]))
    worker_plan = {site: 1 for site, _ in ordered_sites}
    remaining = total_workers - len(worker_plan)
    if remaining < 0:
        raise ValueError('total_workers must be at least the number of active sites')

    while remaining > 0:
        target_site = max(
            worker_plan,
            key=lambda site: site_run_counts[site] / worker_plan[site],
        )
        worker_plan[target_site] += 1
        remaining -= 1
    return worker_plan


def _sort_run(run: dict) -> tuple:
    return (
        run['repeat_index'],
        run['instance_id'],
        run['task_variant'],
    )


def assign_runs_to_workers(runs: list[dict], site_workers: dict[str, int]) -> list[dict]:
    grouped_runs: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        grouped_runs[run['site']].append(run)

    assignments: list[dict] = []
    worker_index = 1
    for site in sorted(site_workers):
        worker_count = site_workers[site]
        site_runs = sorted(grouped_runs.get(site, []), key=_sort_run)
        worker_buckets = [[] for _ in range(worker_count)]
        for index, run in enumerate(site_runs):
            worker_buckets[index % worker_count].append(run)
        for bucket in worker_buckets:
            assignments.append(
                {
                    'worker_id': worker_index,
                    'site': site,
                    'runs': bucket,
                }
            )
            worker_index += 1
    return assignments


def parse_site_workers(value: str | None) -> dict[str, int]:
    if not value:
        return {}
    result: dict[str, int] = {}
    for chunk in value.split(','):
        chunk = chunk.strip()
        if not chunk:
            continue
        site, raw_count = chunk.split('=', 1)
        result[site.strip()] = int(raw_count.strip())
    return result


def get_serial_runs_root() -> Path:
    return Path('agent/gt/runs')


def get_parallel_runs_root(experiment_id: str, attempt_id: str | None = None) -> Path:
    root = Path('agent/gt/runs_parallel') / experiment_id
    if attempt_id:
        return root / attempt_id
    return root


def get_runtime_root(experiment_id: str) -> Path:
    return RUNTIME_DIR / experiment_id


def get_runtime_attempt_root(experiment_id: str, attempt_id: str) -> Path:
    return get_runtime_root(experiment_id) / attempt_id


def get_worker_runtime_dir(experiment_id: str, attempt_id: str, worker_id: int) -> Path:
    return get_runtime_attempt_root(experiment_id, attempt_id) / 'workers' / f'worker-{worker_id}'


def get_worker_auth_state_path(experiment_id: str, attempt_id: str, site: str, worker_id: int, batch_id: int) -> Path:
    return RUNTIME_AUTH_DIR / experiment_id / attempt_id / site / f'worker-{worker_id}' / f'batch-{batch_id}.storage_state.json'


def build_run_id(run: dict, worker_id: int, queue_index: int, batch_id: int) -> str:
    return f'w{worker_id}_q{queue_index}_r{run["repeat_index"]}_b{batch_id}'


def append_status(status_path: Path, payload: dict) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + '\n')


def load_completed_run_keys(status_path: Path) -> set[str]:
    if not status_path.exists():
        return set()
    completed: set[str] = set()
    for line in status_path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if payload.get('status') in {'evaluated_pass', 'evaluated_fail'}:
            completed.add(payload['run_key'])
    return completed
