from __future__ import annotations

from pathlib import Path

from agent.gt.parallel_runner import (
    append_status,
    assign_runs_to_workers,
    build_run_id,
    build_run_key,
    load_completed_run_keys,
    parse_site_workers,
    plan_site_workers,
)


GT_KEYBOARD_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = GT_KEYBOARD_DIR / 'runtime'
RUNTIME_AUTH_DIR = GT_KEYBOARD_DIR / 'auth' / 'runtime'


def get_serial_runs_root() -> Path:
    return Path('agent/gt_keyboard/runs')


def get_parallel_runs_root(experiment_id: str, attempt_id: str | None = None) -> Path:
    root = Path('agent/gt_keyboard/runs_parallel') / experiment_id
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
