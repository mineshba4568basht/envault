"""Tests for envault.reminder."""

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from envault import reminder as rem


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path / "vault")


def test_last_rotated_none_when_never_marked(vault_dir):
    assert rem.last_rotated(vault_dir, "SECRET_KEY") is None


def test_days_since_rotation_none_when_never_marked(vault_dir):
    assert rem.days_since_rotation(vault_dir, "SECRET_KEY") is None


def test_mark_rotated_creates_record(vault_dir):
    rem.mark_rotated(vault_dir, "API_KEY")
    ts = rem.last_rotated(vault_dir, "API_KEY")
    assert ts is not None
    assert isinstance(ts, datetime)


def test_mark_rotated_timestamp_is_recent(vault_dir):
    before = datetime.now(timezone.utc)
    rem.mark_rotated(vault_dir, "DB_PASS")
    after = datetime.now(timezone.utc)
    ts = rem.last_rotated(vault_dir, "DB_PASS")
    assert before <= ts <= after


def test_days_since_rotation_is_near_zero_after_mark(vault_dir):
    rem.mark_rotated(vault_dir, "TOKEN")
    age = rem.days_since_rotation(vault_dir, "TOKEN")
    assert age is not None
    assert 0.0 <= age < 0.01  # less than ~15 minutes


def test_stale_keys_includes_never_rotated(vault_dir):
    keys = ["A", "B"]
    stale = rem.stale_keys(vault_dir, keys, max_age_days=90)
    assert "A" in stale
    assert "B" in stale


def test_stale_keys_excludes_recently_rotated(vault_dir):
    rem.mark_rotated(vault_dir, "FRESH")
    stale = rem.stale_keys(vault_dir, ["FRESH"], max_age_days=90)
    assert "FRESH" not in stale


def test_stale_keys_includes_old_key(vault_dir, monkeypatch):
    """Simulate a key rotated 100 days ago."""
    old_ts = datetime.now(timezone.utc) - timedelta(days=100)
    import json
    from pathlib import Path

    p = rem._reminder_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump({"OLD_KEY": old_ts.strftime(rem._DATE_FMT)}, f)

    stale = rem.stale_keys(vault_dir, ["OLD_KEY"], max_age_days=90)
    assert "OLD_KEY" in stale


def test_clear_reminder_removes_key(vault_dir):
    rem.mark_rotated(vault_dir, "GONE")
    rem.clear_reminder(vault_dir, "GONE")
    assert rem.last_rotated(vault_dir, "GONE") is None


def test_clear_reminder_nonexistent_key_does_not_raise(vault_dir):
    rem.clear_reminder(vault_dir, "NONEXISTENT")  # should not raise


def test_multiple_keys_tracked_independently(vault_dir):
    rem.mark_rotated(vault_dir, "KEY_A")
    rem.mark_rotated(vault_dir, "KEY_B")
    assert rem.last_rotated(vault_dir, "KEY_A") is not None
    assert rem.last_rotated(vault_dir, "KEY_B") is not None
    rem.clear_reminder(vault_dir, "KEY_A")
    assert rem.last_rotated(vault_dir, "KEY_A") is None
    assert rem.last_rotated(vault_dir, "KEY_B") is not None
