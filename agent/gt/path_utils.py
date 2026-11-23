from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any


def windows_long_path(path: Path | str) -> str:
    """Return an OS path string that can address long Windows paths."""
    raw_path = Path(path)
    if os.name != 'nt':
        return str(raw_path)

    raw = str(raw_path)
    if raw.startswith('\\\\?\\'):
        return raw

    absolute = str(raw_path.resolve(strict=False))
    if absolute.startswith('\\\\?\\'):
        return absolute
    if absolute.startswith('\\\\'):
        return '\\\\?\\UNC\\' + absolute[2:]
    return '\\\\?\\' + absolute


def safe_mkdir(path: Path | str) -> None:
    os.makedirs(windows_long_path(path), exist_ok=True)


def safe_copy2(src: Path | str, dst: Path | str) -> None:
    safe_mkdir(Path(dst).parent)
    shutil.copy2(windows_long_path(src), windows_long_path(dst))


def safe_unlink(path: Path | str) -> None:
    try:
        os.unlink(windows_long_path(path))
    except FileNotFoundError:
        pass


def write_text_file(path: Path | str, text: str) -> None:
    path = Path(path)
    safe_mkdir(path.parent)
    with open(windows_long_path(path), 'w', encoding='utf-8') as handle:
        handle.write(text)


def write_json_file(path: Path | str, payload: Any) -> None:
    path = Path(path)
    safe_mkdir(path.parent)
    with open(windows_long_path(path), 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)
        handle.write('\n')
