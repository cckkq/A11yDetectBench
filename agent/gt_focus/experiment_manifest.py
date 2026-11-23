from __future__ import annotations

from pathlib import Path

import yaml


GT_FOCUS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GT_FOCUS_DIR.parent.parent
TASKS_DIR = GT_FOCUS_DIR / 'tasks'


def load_experiment_manifest(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f'Manifest root must be a mapping: {path}')
    return data


def _task_filename(task_base: str, level: str) -> str:
    return f'{task_base}.{level}.yaml'


def _resolve_path(path_text: str | None, base: Path) -> Path | None:
    if not path_text:
        return None
    path = Path(path_text)
    if path.is_absolute():
        return path
    return base / path


def _task_path_for_item(item: dict, task_base: str, level: str, task_root: Path) -> tuple[str, Path]:
    explicit_path = _resolve_path(item.get('task_path'), PROJECT_ROOT)
    if explicit_path is not None:
        return explicit_path.name, explicit_path
    task_file = item.get('task_file') or _task_filename(task_base, level)
    return task_file, task_root / task_file


def _load_task_yaml(task_path: Path) -> dict:
    task_yaml = yaml.safe_load(task_path.read_text(encoding='utf-8'))
    if not isinstance(task_yaml, dict):
        raise ValueError(f'Task file root must be a mapping: {task_path}')
    task_id = task_yaml.get('task_id')
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError(f'Task file missing task_id: {task_path}')
    return task_yaml


def expand_runs(manifest: dict) -> list[dict]:
    defaults = manifest['defaults']
    levels = defaults['levels']
    default_max_steps = defaults['max_steps']
    default_repeats = defaults['repeats']
    default_task_root = _resolve_path(defaults.get('task_root'), PROJECT_ROOT) or TASKS_DIR

    runs: list[dict] = []
    for site, items in manifest['sites'].items():
        for item in items:
            task_base = item['task_base']
            if not task_base.startswith(f'{site}.'):
                raise ValueError(f'task_base {task_base!r} does not match site {site!r}')

            max_steps = item.get('max_steps', default_max_steps)
            repeats = item.get('repeats', default_repeats)
            item_levels = item.get('levels', levels)
            task_root = _resolve_path(item.get('task_root'), PROJECT_ROOT) or default_task_root

            for level in item_levels:
                task_file, task_path = _task_path_for_item(item, task_base, level, task_root)
                if not task_path.exists():
                    raise FileNotFoundError(f'Task file not found for manifest entry: {task_path}')

                task_yaml = _load_task_yaml(task_path)
                task_id = task_yaml['task_id']
                if not task_id.endswith(level):
                    raise ValueError(f'Task id {task_id!r} does not match manifest level {level!r}: {task_path}')
                auth_required = 'auth_state_file' in task_yaml and task_yaml['auth_state_file'] is not None

                for repeat_index in range(1, repeats + 1):
                    runs.append(
                        {
                            'site': site,
                            'instance_id': task_base,
                            'task_id': task_id,
                            'task_base': task_base,
                            'task_variant': level,
                            'task_file': task_file,
                            'task_path': str(task_path.resolve()),
                            'max_steps': max_steps,
                            'repeat_index': repeat_index,
                            'auth_required': auth_required,
                        }
                    )
    return runs
