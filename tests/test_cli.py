"""Tests for the envault CLI."""

import pytest
from click.testing import CliRunner
from envault.cli import cli


VAULT_PASSWORD = "test-password-123"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path / "test_vault")


def invoke_set(runner, vault_dir, key, value, password=VAULT_PASSWORD):
    return runner.invoke(
        cli,
        ["set", key, value, "--vault", vault_dir, "--password", password, "--password", password],
    )


def invoke_get(runner, vault_dir, key, password=VAULT_PASSWORD):
    return runner.invoke(cli, ["get", key, "--vault", vault_dir, "--password", password])


def invoke_delete(runner, vault_dir, key, password=VAULT_PASSWORD):
    return runner.invoke(cli, ["delete", key, "--vault", vault_dir, "--password", password])


def invoke_list(runner, vault_dir, password=VAULT_PASSWORD):
    return runner.invoke(cli, ["list", "--vault", vault_dir, "--password", password])


def test_set_and_get_secret(runner, vault_dir):
    result = invoke_set(runner, vault_dir, "DB_URL", "postgres://localhost/db")
    assert result.exit_code == 0
    assert "DB_URL" in result.output

    result = invoke_get(runner, vault_dir, "DB_URL")
    assert result.exit_code == 0
    assert "postgres://localhost/db" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    invoke_set(runner, vault_dir, "EXISTING", "value")
    result = invoke_get(runner, vault_dir, "MISSING_KEY")
    assert result.exit_code != 0


def test_delete_secret(runner, vault_dir):
    invoke_set(runner, vault_dir, "TOKEN", "abc123")
    result = invoke_delete(runner, vault_dir, "TOKEN")
    assert result.exit_code == 0
    assert "TOKEN" in result.output

    result = invoke_get(runner, vault_dir, "TOKEN")
    assert result.exit_code != 0


def test_delete_missing_key_exits_nonzero(runner, vault_dir):
    invoke_set(runner, vault_dir, "SOME_KEY", "val")
    result = invoke_delete(runner, vault_dir, "NONEXISTENT")
    assert result.exit_code != 0


def test_list_secrets(runner, vault_dir):
    invoke_set(runner, vault_dir, "KEY_A", "val_a")
    invoke_set(runner, vault_dir, "KEY_B", "val_b")
    result = invoke_list(runner, vault_dir)
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = invoke_list(runner, vault_dir)
    assert result.exit_code == 0
    assert "No secrets" in result.output
