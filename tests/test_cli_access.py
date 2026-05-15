"""Tests for the CLI access control commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.cli import cli
from envault import access


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    d = tmp_path / "vault"
    d.mkdir()
    return d


def _invoke(runner, vault_dir, *args):
    return runner.invoke(
        cli,
        ["--vault-dir", str(vault_dir), "--password", "testpass"] + list(args),
    )


def test_grant_command_output(runner, vault_dir):
    result = _invoke(runner, vault_dir, "access", "grant", "MY_KEY", "read")
    assert result.exit_code == 0
    assert "Granted 'read' on 'MY_KEY'" in result.output


def test_revoke_command_output(runner, vault_dir):
    _invoke(runner, vault_dir, "access", "grant", "MY_KEY", "write")
    result = _invoke(runner, vault_dir, "access", "revoke", "MY_KEY", "write")
    assert result.exit_code == 0
    assert "Revoked 'write' on 'MY_KEY'" in result.output


def test_show_command_default(runner, vault_dir):
    result = _invoke(runner, vault_dir, "access", "show", "SOME_KEY")
    assert result.exit_code == 0
    assert "SOME_KEY" in result.output
    assert "read" in result.output
    assert "write" in result.output


def test_show_command_after_revoke(runner, vault_dir):
    _invoke(runner, vault_dir, "access", "revoke", "LOCKED", "write")
    result = _invoke(runner, vault_dir, "access", "show", "LOCKED")
    assert result.exit_code == 0
    assert "write" not in result.output


def test_list_command_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "access", "list")
    assert result.exit_code == 0
    assert "No explicit access rules" in result.output


def test_list_command_shows_restricted_keys(runner, vault_dir):
    _invoke(runner, vault_dir, "access", "revoke", "DB_PASS", "write")
    result = _invoke(runner, vault_dir, "access", "list")
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
