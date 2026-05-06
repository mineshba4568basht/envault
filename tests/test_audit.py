"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import record, read, clear, AUDIT_FILENAME


@pytest.fixture
def audit_dir(tmp_path):
    return str(tmp_path / "vault")


def test_record_creates_log_file(audit_dir):
    record(audit_dir, "set", "DB_PASSWORD", actor="alice")
    assert (Path(audit_dir) / AUDIT_FILENAME).exists()


def test_record_single_entry(audit_dir):
    record(audit_dir, "set", "API_KEY", actor="bob")
    entries = read(audit_dir)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["action"] == "set"
    assert entry["key"] == "API_KEY"
    assert entry["actor"] == "bob"
    assert "timestamp" in entry


def test_record_multiple_entries(audit_dir):
    record(audit_dir, "set", "KEY_A", actor="alice")
    record(audit_dir, "get", "KEY_A", actor="bob")
    record(audit_dir, "delete", "KEY_A", actor="alice")
    entries = read(audit_dir)
    assert len(entries) == 3
    assert entries[0]["action"] == "set"
    assert entries[1]["action"] == "get"
    assert entries[2]["action"] == "delete"


def test_read_returns_empty_list_when_no_log(audit_dir):
    entries = read(audit_dir)
    assert entries == []


def test_clear_removes_log(audit_dir):
    record(audit_dir, "set", "SECRET", actor="carol")
    assert (Path(audit_dir) / AUDIT_FILENAME).exists()
    clear(audit_dir)
    assert not (Path(audit_dir) / AUDIT_FILENAME).exists()


def test_clear_is_safe_when_no_log(audit_dir):
    # Should not raise even if the log does not exist
    clear(audit_dir)


def test_record_uses_env_user_as_default_actor(audit_dir, monkeypatch):
    monkeypatch.setenv("USER", "devuser")
    record(audit_dir, "set", "TOKEN")
    entries = read(audit_dir)
    assert entries[0]["actor"] == "devuser"


def test_timestamp_is_iso_format(audit_dir):
    record(audit_dir, "get", "SOME_KEY", actor="tester")
    entries = read(audit_dir)
    ts = entries[0]["timestamp"]
    # Basic ISO 8601 check
    assert "T" in ts
    assert "+" in ts or ts.endswith("Z") or "00:00" in ts
