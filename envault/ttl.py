"""TTL (time-to-live) support for vault secrets."""

import json
import time
from pathlib import Path
from typing import Optional


def _ttl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".ttl.json"


def _load_ttl(vault_dir: str) -> dict:
    path = _ttl_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_ttl(vault_dir: str, data: dict) -> None:
    path = _ttl_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def set_ttl(vault_dir: str, key: str, seconds: int) -> None:
    """Set a TTL for a key. The key expires after `seconds` from now."""
    data = _load_ttl(vault_dir)
    data[key] = time.time() + seconds
    _save_ttl(vault_dir, data)


def clear_ttl(vault_dir: str, key: str) -> None:
    """Remove TTL for a key (makes it permanent)."""
    data = _load_ttl(vault_dir)
    data.pop(key, None)
    _save_ttl(vault_dir, data)


def is_expired(vault_dir: str, key: str) -> bool:
    """Return True if the key has a TTL that has passed."""
    data = _load_ttl(vault_dir)
    if key not in data:
        return False
    return time.time() > data[key]


def get_ttl(vault_dir: str, key: str) -> Optional[float]:
    """Return seconds remaining for a key, or None if no TTL is set."""
    data = _load_ttl(vault_dir)
    if key not in data:
        return None
    remaining = data[key] - time.time()
    return max(remaining, 0.0)


def purge_expired(vault_dir: str) -> list:
    """Remove expired TTL entries and return list of expired keys."""
    data = _load_ttl(vault_dir)
    now = time.time()
    expired = [k for k, exp in data.items() if now > exp]
    for k in expired:
        del data[k]
    _save_ttl(vault_dir, data)
    return expired
