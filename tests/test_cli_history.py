"""Tests for the history / rollback CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_history import history_cmd, rollback_cmd

PASSWORD = "cli-hist-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path / "vault")


def _set(runner, vault_dir, key, value):
    from envault.cli import set_secret
    return runner.invoke(
        set_secret,
        ["--vault-dir", vault_dir, "--password", PASSWORD, key, value],
    )


def test_history_shows_entries(runner, vault_dir):
    _set(runner, vault_dir, "API_KEY", "aaa")
    _set(runner, vault_dir, "API_KEY", "bbb")
    result = runner.invoke(
        history_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, "API_KEY"],
    )
    assert result.exit_code == 0
    assert "[0]" in result.output
    assert "[1]" in result.output


def test_history_no_entries_message(runner, vault_dir):
    result = runner.invoke(
        history_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, "MISSING_KEY"],
    )
    assert result.exit_code == 0
    assert "No history" in result.output


def test_rollback_restores_previous_value(runner, vault_dir):
    _set(runner, vault_dir, "TOKEN", "first-value")
    _set(runner, vault_dir, "TOKEN", "second-value")

    result = runner.invoke(
        rollback_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, "TOKEN", "0"],
    )
    assert result.exit_code == 0
    assert "Rolled back" in result.output

    from envault.vault import Vault
    v = Vault(vault_dir, PASSWORD)
    assert v.get("TOKEN") == "first-value"


def test_rollback_invalid_version_exits_nonzero(runner, vault_dir):
    _set(runner, vault_dir, "TOKEN", "only")
    result = runner.invoke(
        rollback_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, "TOKEN", "99"],
    )
    assert result.exit_code != 0
