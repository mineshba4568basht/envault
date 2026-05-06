"""Audit log for vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = "audit.log"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit_path(vault_dir: str) -> Path:
    return Path(vault_dir) / AUDIT_FILENAME


def record(vault_dir: str, action: str, key: str, actor: Optional[str] = None) -> None:
    """Append a single audit entry to the vault's audit log."""
    entry = {
        "timestamp": _timestamp(),
        "action": action,
        "key": key,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    path = _audit_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read(vault_dir: str) -> List[dict]:
    """Return all audit log entries as a list of dicts."""
    path = _audit_path(vault_dir)
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def clear(vault_dir: str) -> None:
    """Remove the audit log file entirely."""
    path = _audit_path(vault_dir)
    if path.exists():
        path.unlink()
