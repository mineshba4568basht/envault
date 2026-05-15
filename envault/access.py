"""Access control: per-key read/write permissions for vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set

READ = "read"
WRITE = "write"
VALID_PERMS = {READ, WRITE}


def _access_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".access.json"


def _load_access(vault_dir: str) -> Dict[str, List[str]]:
    path = _access_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_access(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = _access_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def grant(vault_dir: str, key: str, permission: str) -> None:
    """Grant a permission (read/write) to a key."""
    if permission not in VALID_PERMS:
        raise ValueError(f"Invalid permission '{permission}'. Must be one of {VALID_PERMS}")
    data = _load_access(vault_dir)
    perms: Set[str] = set(data.get(key, []))
    perms.add(permission)
    data[key] = sorted(perms)
    _save_access(vault_dir, data)


def revoke(vault_dir: str, key: str, permission: str) -> None:
    """Revoke a permission from a key."""
    if permission not in VALID_PERMS:
        raise ValueError(f"Invalid permission '{permission}'. Must be one of {VALID_PERMS}")
    data = _load_access(vault_dir)
    perms: Set[str] = set(data.get(key, []))
    perms.discard(permission)
    if perms:
        data[key] = sorted(perms)
    else:
        data.pop(key, None)
    _save_access(vault_dir, data)


def get_permissions(vault_dir: str, key: str) -> List[str]:
    """Return the list of permissions for a key."""
    data = _load_access(vault_dir)
    return data.get(key, [READ, WRITE])  # default: full access


def can_read(vault_dir: str, key: str) -> bool:
    return READ in get_permissions(vault_dir, key)


def can_write(vault_dir: str, key: str) -> bool:
    return WRITE in get_permissions(vault_dir, key)


def list_restricted_keys(vault_dir: str) -> Dict[str, List[str]]:
    """Return all keys with explicit (non-default) access rules."""
    return dict(_load_access(vault_dir))


def clear_permissions(vault_dir: str, key: str) -> None:
    """Remove all explicit permissions for a key (resets to default)."""
    data = _load_access(vault_dir)
    data.pop(key, None)
    _save_access(vault_dir, data)
