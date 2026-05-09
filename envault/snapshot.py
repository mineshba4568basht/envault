"""Snapshot module: capture and restore full vault state."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import Vault


def _snapshots_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".snapshots.json"


def _load_snapshots(vault_dir: str) -> List[dict]:
    path = _snapshots_path(vault_dir)
    if not path.exists():
        return []
    with path.open("r") as f:
        return json.load(f)


def _save_snapshots(vault_dir: str, snapshots: List[dict]) -> None:
    path = _snapshots_path(vault_dir)
    with path.open("w") as f:
        json.dump(snapshots, f, indent=2)


def take_snapshot(vault: Vault, label: Optional[str] = None) -> str:
    """Capture the current state of the vault and store it.

    Returns the snapshot ID (timestamp-based).
    """
    keys = vault.list()
    data: Dict[str, str] = {}
    for key in keys:
        data[key] = vault.get(key)

    snapshot_id = str(int(time.time() * 1000))
    entry = {
        "id": snapshot_id,
        "label": label or "",
        "timestamp": time.time(),
        "data": data,
    }

    snapshots = _load_snapshots(vault.storage.vault_dir)
    snapshots.append(entry)
    _save_snapshots(vault.storage.vault_dir, snapshots)
    return snapshot_id


def list_snapshots(vault_dir: str) -> List[dict]:
    """Return all snapshots metadata (without secret data)."""
    snapshots = _load_snapshots(vault_dir)
    return [
        {"id": s["id"], "label": s["label"], "timestamp": s["timestamp"]}
        for s in snapshots
    ]


def restore_snapshot(vault: Vault, snapshot_id: str) -> int:
    """Restore vault to a previous snapshot state.

    Overwrites all current keys with snapshot values.
    Returns the number of keys restored.
    """
    snapshots = _load_snapshots(vault.storage.vault_dir)
    entry = next((s for s in snapshots if s["id"] == snapshot_id), None)
    if entry is None:
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")

    for key, value in entry["data"].items():
        vault.set(key, value)

    return len(entry["data"])


def delete_snapshot(vault_dir: str, snapshot_id: str) -> None:
    """Remove a snapshot by ID."""
    snapshots = _load_snapshots(vault_dir)
    new_snapshots = [s for s in snapshots if s["id"] != snapshot_id]
    if len(new_snapshots) == len(snapshots):
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")
    _save_snapshots(vault_dir, new_snapshots)
