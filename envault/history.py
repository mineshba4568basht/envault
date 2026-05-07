"""Secret history tracking — records versioned snapshots of secret values."""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


def _history_path(vault_dir: str, key: str) -> Path:
    safe_key = key.replace("/", "__").replace("\\", "__")
    return Path(vault_dir) / ".history" / f"{safe_key}.json"


def record_change(vault_dir: str, key: str, encrypted_value: bytes, action: str = "set") -> None:
    """Append a versioned entry for *key* to its history log."""
    path = _history_path(vault_dir, key)
    path.parent.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, Any]] = []
    if path.exists():
        entries = json.loads(path.read_text())

    entries.append({
        "ts": time.time(),
        "action": action,
        "value": encrypted_value.hex(),
    })

    path.write_text(json.dumps(entries, indent=2))


def get_history(vault_dir: str, key: str) -> List[Dict[str, Any]]:
    """Return all history entries for *key*, oldest first."""
    path = _history_path(vault_dir, key)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def get_version(vault_dir: str, key: str, version: int) -> Optional[bytes]:
    """Return the encrypted value bytes for a specific history *version* (0-indexed)."""
    entries = get_history(vault_dir, key)
    if version < 0 or version >= len(entries):
        raise IndexError(f"Version {version} does not exist for key '{key}' (total: {len(entries)})")
    return bytes.fromhex(entries[version]["value"])


def clear_history(vault_dir: str, key: str) -> None:
    """Delete the history log for *key*."""
    path = _history_path(vault_dir, key)
    if path.exists():
        path.unlink()
