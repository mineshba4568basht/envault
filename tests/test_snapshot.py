"""Tests for envault.snapshot module."""

import time
import pytest

from envault.vault import Vault
from envault.snapshot import (
    take_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)


PASSWORD = "test-password"


@pytest.fixture
def tmp_vault(tmp_path):
    vault = Vault(str(tmp_path), PASSWORD)
    vault.set("KEY1", "value1")
    vault.set("KEY2", "value2")
    return vault


def test_take_snapshot_returns_string_id(tmp_vault):
    snapshot_id = take_snapshot(tmp_vault)
    assert isinstance(snapshot_id, str)
    assert len(snapshot_id) > 0


def test_take_snapshot_with_label(tmp_vault):
    take_snapshot(tmp_vault, label="before-deploy")
    snapshots = list_snapshots(tmp_vault.storage.vault_dir)
    assert len(snapshots) == 1
    assert snapshots[0]["label"] == "before-deploy"


def test_list_snapshots_empty(tmp_path):
    result = list_snapshots(str(tmp_path))
    assert result == []


def test_list_snapshots_multiple(tmp_vault):
    take_snapshot(tmp_vault, label="snap1")
    time.sleep(0.01)
    take_snapshot(tmp_vault, label="snap2")
    snapshots = list_snapshots(tmp_vault.storage.vault_dir)
    assert len(snapshots) == 2
    labels = [s["label"] for s in snapshots]
    assert "snap1" in labels
    assert "snap2" in labels


def test_list_snapshots_does_not_expose_secret_data(tmp_vault):
    take_snapshot(tmp_vault)
    snapshots = list_snapshots(tmp_vault.storage.vault_dir)
    for snap in snapshots:
        assert "data" not in snap


def test_restore_snapshot_overwrites_current_state(tmp_vault):
    snapshot_id = take_snapshot(tmp_vault)
    tmp_vault.set("KEY1", "changed")
    tmp_vault.set("KEY3", "new-key")

    count = restore_snapshot(tmp_vault, snapshot_id)

    assert count == 2
    assert tmp_vault.get("KEY1") == "value1"
    assert tmp_vault.get("KEY2") == "value2"


def test_restore_snapshot_unknown_id_raises(tmp_vault):
    with pytest.raises(KeyError, match="not found"):
        restore_snapshot(tmp_vault, "nonexistent-id")


def test_restore_snapshot_returns_key_count(tmp_vault):
    snapshot_id = take_snapshot(tmp_vault)
    count = restore_snapshot(tmp_vault, snapshot_id)
    assert count == 2


def test_delete_snapshot_removes_entry(tmp_vault):
    snapshot_id = take_snapshot(tmp_vault)
    delete_snapshot(tmp_vault.storage.vault_dir, snapshot_id)
    snapshots = list_snapshots(tmp_vault.storage.vault_dir)
    assert all(s["id"] != snapshot_id for s in snapshots)


def test_delete_snapshot_unknown_id_raises(tmp_vault):
    with pytest.raises(KeyError, match="not found"):
        delete_snapshot(tmp_vault.storage.vault_dir, "bad-id")
