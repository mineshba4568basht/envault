"""Pin/unpin secrets to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _pin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".pins.json"


def _load_pins(vault_dir: str) -> dict:
    p = _pin_path(vault_dir)
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)


def _save_pins(vault_dir: str, data: dict) -> None:
    p = _pin_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def pin(vault_dir: str, key: str) -> None:
    """Pin a secret key so it cannot be overwritten or deleted."""
    data = _load_pins(vault_dir)
    data[key] = True
    _save_pins(vault_dir, data)


def unpin(vault_dir: str, key: str) -> None:
    """Unpin a secret key, allowing modifications again."""
    data = _load_pins(vault_dir)
    data.pop(key, None)
    _save_pins(vault_dir, data)


def is_pinned(vault_dir: str, key: str) -> bool:
    """Return True if the given key is pinned."""
    data = _load_pins(vault_dir)
    return data.get(key, False)


def list_pinned(vault_dir: str) -> List[str]:
    """Return a sorted list of all pinned keys."""
    data = _load_pins(vault_dir)
    return sorted(k for k, v in data.items() if v)


def clear_pins(vault_dir: str) -> None:
    """Remove all pins."""
    _save_pins(vault_dir, {})


class PinnedKeyError(Exception):
    """Raised when an operation is attempted on a pinned key."""

    def __init__(self, key: str):
        super().__init__(f"Key '{key}' is pinned and cannot be modified or deleted.")
        self.key = key
