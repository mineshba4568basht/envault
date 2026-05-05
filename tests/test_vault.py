"""Tests for the Vault high-level interface and VaultStorage backend."""

import pytest

from envault.storage import VaultStorage
from envault.vault import Vault


@pytest.fixture
def tmp_vault(tmp_path):
    """Return a Vault backed by a temporary directory."""
    storage = VaultStorage(vault_dir=tmp_path)
    return Vault(password="test-password-123", storage=storage)


def test_set_and_get_secret(tmp_vault):
    tmp_vault.set("DB_URL", "postgres://localhost/mydb")
    assert tmp_vault.get("DB_URL") == "postgres://localhost/mydb"


def test_get_missing_key_raises(tmp_vault):
    with pytest.raises(KeyError, match="SECRET_KEY"):
        tmp_vault.get("SECRET_KEY")


def test_delete_secret(tmp_vault):
    tmp_vault.set("TOKEN", "abc123")
    tmp_vault.delete("TOKEN")
    with pytest.raises(KeyError):
        tmp_vault.get("TOKEN")


def test_delete_missing_key_raises(tmp_vault):
    with pytest.raises(KeyError):
        tmp_vault.delete("NONEXISTENT")


def test_list_keys_empty(tmp_vault):
    assert tmp_vault.list_keys() == []


def test_list_keys_sorted(tmp_vault):
    tmp_vault.set("ZEBRA", "z")
    tmp_vault.set("ALPHA", "a")
    tmp_vault.set("MANGO", "m")
    assert tmp_vault.list_keys() == ["ALPHA", "MANGO", "ZEBRA"]


def test_export_env(tmp_vault):
    tmp_vault.set("KEY1", "value1")
    tmp_vault.set("KEY2", "value2")
    exported = tmp_vault.export_env()
    assert exported == {"KEY1": "value1", "KEY2": "value2"}


def test_wrong_password_raises_on_get(tmp_path):
    storage = VaultStorage(vault_dir=tmp_path)
    vault_writer = Vault(password="correct", storage=storage)
    vault_writer.set("API_KEY", "supersecret")

    vault_reader = Vault(password="wrong", storage=storage)
    with pytest.raises(Exception):
        vault_reader.get("API_KEY")


def test_vault_file_has_restricted_permissions(tmp_path):
    import stat

    storage = VaultStorage(vault_dir=tmp_path)
    vault = Vault(password="pass", storage=storage)
    vault.set("X", "y")

    mode = stat.S_IMODE(storage.vault_path.stat().st_mode)
    assert mode == 0o600
