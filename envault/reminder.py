"""Secret rotation reminders: warn when secrets haven't been rotated recently."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _reminder_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".reminder.json"


def _load(vault_dir: str) -> dict:
    p = _reminder_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save(vault_dir: str, data: dict) -> None:
    p = _reminder_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def mark_rotated(vault_dir: str, key: str) -> None:
    """Record that *key* was rotated right now."""
    data = _load(vault_dir)
    data[key] = datetime.now(timezone.utc).strftime(_DATE_FMT)
    _save(vault_dir, data)


def last_rotated(vault_dir: str, key: str) -> Optional[datetime]:
    """Return the last rotation datetime for *key*, or None if never recorded."""
    data = _load(vault_dir)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.strptime(raw, _DATE_FMT).replace(tzinfo=timezone.utc)


def days_since_rotation(vault_dir: str, key: str) -> Optional[float]:
    """Return the number of days since *key* was last rotated, or None."""
    ts = last_rotated(vault_dir, key)
    if ts is None:
        return None
    delta = datetime.now(timezone.utc) - ts
    return delta.total_seconds() / 86400


def stale_keys(vault_dir: str, keys: list[str], max_age_days: float = 90.0) -> list[str]:
    """Return keys that are overdue for rotation (never rotated or older than *max_age_days*)."""
    result = []
    for key in keys:
        age = days_since_rotation(vault_dir, key)
        if age is None or age >= max_age_days:
            result.append(key)
    return result


def clear_reminder(vault_dir: str, key: str) -> None:
    """Remove rotation record for *key*."""
    data = _load(vault_dir)
    data.pop(key, None)
    _save(vault_dir, data)
