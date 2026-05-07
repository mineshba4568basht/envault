"""Tests for the CLI TTL commands (ttl-set, ttl-get, ttl-purge)."""

import os
import time
import pytest
from click.testing import CliRunner
from envault.cli import cli
from envault.vault import Vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def _set(runner, vault_dir, key, value, password="pass"):
    """Helper to set a secret via CLI."""
    return runner.invoke(
        cli,
        ["--vault-dir", vault_dir, "--password", password, "set", key, value],
    )


def _ttl_set(runner, vault_dir, key, seconds, password="pass"):
    """Helper to invoke ttl-set via CLI."""
    return runner.invoke(
        cli,
        ["--vault-dir", vault_dir, "--password", password, "ttl-set", key, str(seconds)],
    )


def _ttl_get(runner, vault_dir, key, password="pass"):
    """Helper to invoke ttl-get via CLI."""
    return runner.invoke(
        cli,
        ["--vault-dir", vault_dir, "--password", password, "ttl-get", key],
    )


def _ttl_purge(runner, vault_dir, password="pass"):
    """Helper to invoke ttl-purge via CLI."""
    return runner.invoke(
        cli,
        ["--vault-dir", vault_dir, "--password", password, "ttl-purge"],
    )


def test_ttl_set_success(runner, vault_dir):
    _set(runner, vault_dir, "API_KEY", "abc123")
    result = _ttl_set(runner, vault_dir, "API_KEY", 3600)
    assert result.exit_code == 0
    assert "TTL set" in result.output
    assert "API_KEY" in result.output


def test_ttl_get_shows_remaining(runner, vault_dir):
    _set(runner, vault_dir, "TOKEN", "xyz")
    _ttl_set(runner, vault_dir, "TOKEN", 3600)
    result = _ttl_get(runner, vault_dir, "TOKEN")
    assert result.exit_code == 0
    assert "TOKEN" in result.output
    # Should display some positive remaining time
    assert "s" in result.output or "remaining" in result.output.lower()


def test_ttl_get_no_ttl_set(runner, vault_dir):
    _set(runner, vault_dir, "NO_TTL", "value")
    result = _ttl_get(runner, vault_dir, "NO_TTL")
    assert result.exit_code == 0
    assert "no ttl" in result.output.lower() or "never" in result.output.lower()


def test_ttl_get_expired_key(runner, vault_dir):
    _set(runner, vault_dir, "TEMP", "ephemeral")
    _ttl_set(runner, vault_dir, "TEMP", 1)
    time.sleep(1.1)
    result = _ttl_get(runner, vault_dir, "TEMP")
    assert result.exit_code == 0
    assert "expired" in result.output.lower()


def test_ttl_purge_removes_expired_keys(runner, vault_dir):
    # Set two secrets: one with a very short TTL, one with a long TTL
    _set(runner, vault_dir, "SHORT", "gone")
    _set(runner, vault_dir, "LONG", "stays")
    _ttl_set(runner, vault_dir, "SHORT", 1)
    _ttl_set(runner, vault_dir, "LONG", 9999)

    time.sleep(1.1)

    result = _ttl_purge(runner, vault_dir)
    assert result.exit_code == 0
    assert "SHORT" in result.output or "1" in result.output

    # Verify SHORT is gone and LONG remains
    vault = Vault(vault_dir, "pass")
    from envault.vault import KeyNotFoundError
    with pytest.raises(KeyNotFoundError):
        vault.get("SHORT")
    assert vault.get("LONG") == "stays"


def test_ttl_purge_no_expired_keys(runner, vault_dir):
    _set(runner, vault_dir, "PERMANENT", "value")
    result = _ttl_purge(runner, vault_dir)
    assert result.exit_code == 0
    assert "0" in result.output or "no expired" in result.output.lower()


def test_ttl_set_invalid_seconds(runner, vault_dir):
    _set(runner, vault_dir, "KEY", "val")
    result = _ttl_set(runner, vault_dir, "KEY", -10)
    # Should fail or warn about non-positive TTL
    assert result.exit_code != 0 or "invalid" in result.output.lower() or "error" in result.output.lower()
