"""Tests for envault.ttl module."""

import time
import pytest
from pathlib import Path
from envault import ttl as ttl_mod


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_no_ttl_returns_none(vault_dir):
    assert ttl_mod.get_ttl(vault_dir, "MY_KEY") is None


def test_no_ttl_not_expired(vault_dir):
    assert ttl_mod.is_expired(vault_dir, "MY_KEY") is False


def test_set_ttl_creates_file(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", 60)
    assert (Path(vault_dir) / ".ttl.json").exists()


def test_set_ttl_remaining_positive(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", 60)
    remaining = ttl_mod.get_ttl(vault_dir, "KEY")
    assert remaining is not None
    assert 55 < remaining <= 60


def test_set_ttl_not_yet_expired(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", 60)
    assert ttl_mod.is_expired(vault_dir, "KEY") is False


def test_expired_key_detected(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", -1)  # already in the past
    assert ttl_mod.is_expired(vault_dir, "KEY") is True


def test_expired_remaining_is_zero(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", -10)
    assert ttl_mod.get_ttl(vault_dir, "KEY") == 0.0


def test_clear_ttl_removes_key(vault_dir):
    ttl_mod.set_ttl(vault_dir, "KEY", 60)
    ttl_mod.clear_ttl(vault_dir, "KEY")
    assert ttl_mod.get_ttl(vault_dir, "KEY") is None


def test_clear_ttl_nonexistent_is_noop(vault_dir):
    ttl_mod.clear_ttl(vault_dir, "MISSING")  # should not raise


def test_purge_expired_returns_expired_keys(vault_dir):
    ttl_mod.set_ttl(vault_dir, "OLD", -5)
    ttl_mod.set_ttl(vault_dir, "FRESH", 300)
    expired = ttl_mod.purge_expired(vault_dir)
    assert "OLD" in expired
    assert "FRESH" not in expired


def test_purge_expired_removes_from_store(vault_dir):
    ttl_mod.set_ttl(vault_dir, "OLD", -5)
    ttl_mod.purge_expired(vault_dir)
    assert ttl_mod.get_ttl(vault_dir, "OLD") is None


def test_purge_expired_keeps_valid_keys(vault_dir):
    ttl_mod.set_ttl(vault_dir, "FRESH", 300)
    ttl_mod.purge_expired(vault_dir)
    assert ttl_mod.get_ttl(vault_dir, "FRESH") is not None


def test_purge_no_entries_returns_empty(vault_dir):
    assert ttl_mod.purge_expired(vault_dir) == []
