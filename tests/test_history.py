"""Tests for envault.history — versioned secret snapshots."""

import pytest
from pathlib import Path

from envault.history import record_change, get_history, get_version, clear_history
from envault.crypto import encrypt, decrypt

PASSWORD = "hist-test-pass"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path / "vault")


def _enc(value: str) -> bytes:
    return encrypt(value, PASSWORD)


# ---------------------------------------------------------------------------
# record_change / get_history
# ---------------------------------------------------------------------------

def test_record_creates_history_file(vault_dir):
    record_change(vault_dir, "MY_KEY", _enc("v1"))
    history_file = Path(vault_dir) / ".history" / "MY_KEY.json"
    assert history_file.exists()


def test_get_history_returns_empty_for_unknown_key(vault_dir):
    assert get_history(vault_dir, "MISSING") == []


def test_get_history_single_entry(vault_dir):
    record_change(vault_dir, "K", _enc("hello"), action="set")
    entries = get_history(vault_dir, "K")
    assert len(entries) == 1
    assert entries[0]["action"] == "set"


def test_get_history_multiple_entries_ordered(vault_dir):
    record_change(vault_dir, "K", _enc("v1"), action="set")
    record_change(vault_dir, "K", _enc("v2"), action="set")
    record_change(vault_dir, "K", _enc("v2"), action="delete")
    entries = get_history(vault_dir, "K")
    assert len(entries) == 3
    assert entries[2]["action"] == "delete"


# ---------------------------------------------------------------------------
# get_version
# ---------------------------------------------------------------------------

def test_get_version_returns_correct_encrypted_bytes(vault_dir):
    enc_v1 = _enc("secret-one")
    enc_v2 = _enc("secret-two")
    record_change(vault_dir, "K", enc_v1)
    record_change(vault_dir, "K", enc_v2)

    retrieved = get_version(vault_dir, "K", 0)
    assert decrypt(retrieved, PASSWORD) == "secret-one"


def test_get_version_out_of_range_raises(vault_dir):
    record_change(vault_dir, "K", _enc("only"))
    with pytest.raises(IndexError):
        get_version(vault_dir, "K", 5)


# ---------------------------------------------------------------------------
# clear_history
# ---------------------------------------------------------------------------

def test_clear_history_removes_file(vault_dir):
    record_change(vault_dir, "K", _enc("v"))
    clear_history(vault_dir, "K")
    assert get_history(vault_dir, "K") == []


def test_clear_history_noop_when_no_file(vault_dir):
    clear_history(vault_dir, "NONEXISTENT")  # should not raise


# ---------------------------------------------------------------------------
# Integration: Vault auto-records history
# ---------------------------------------------------------------------------

def test_vault_set_records_history(tmp_path):
    from envault.vault import Vault
    v = Vault(str(tmp_path / "v"), PASSWORD, track_history=True)
    v.set("DB_URL", "postgres://localhost/dev")
    v.set("DB_URL", "postgres://localhost/prod")
    entries = get_history(str(tmp_path / "v"), "DB_URL")
    assert len(entries) == 2
