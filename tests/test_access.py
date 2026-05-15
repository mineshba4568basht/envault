"""Tests for envault.access — per-key permission control."""

import pytest
from pathlib import Path
from envault import access


@pytest.fixture
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path / "vault")


def test_default_permissions_are_read_and_write(vault_dir):
    perms = access.get_permissions(vault_dir, "MY_KEY")
    assert "read" in perms
    assert "write" in perms


def test_can_read_default_true(vault_dir):
    assert access.can_read(vault_dir, "MY_KEY") is True


def test_can_write_default_true(vault_dir):
    assert access.can_write(vault_dir, "MY_KEY") is True


def test_grant_read_only(vault_dir):
    access.revoke(vault_dir, "SECRET", "write")
    assert access.can_read(vault_dir, "SECRET") is True
    assert access.can_write(vault_dir, "SECRET") is False


def test_grant_permission_is_idempotent(vault_dir):
    access.grant(vault_dir, "KEY", "read")
    access.grant(vault_dir, "KEY", "read")
    perms = access.get_permissions(vault_dir, "KEY")
    assert perms.count("read") == 1


def test_revoke_write_permission(vault_dir):
    access.grant(vault_dir, "KEY", "write")
    access.revoke(vault_dir, "KEY", "write")
    assert access.can_write(vault_dir, "KEY") is False


def test_revoke_nonexistent_permission_does_not_raise(vault_dir):
    access.revoke(vault_dir, "KEY", "write")  # no explicit perms set yet
    # no exception expected


def test_invalid_permission_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid permission"):
        access.grant(vault_dir, "KEY", "admin")


def test_list_restricted_keys_empty(vault_dir):
    assert access.list_restricted_keys(vault_dir) == {}


def test_list_restricted_keys_shows_entries(vault_dir):
    access.revoke(vault_dir, "DB_PASS", "write")
    restricted = access.list_restricted_keys(vault_dir)
    assert "DB_PASS" in restricted


def test_clear_permissions_resets_to_default(vault_dir):
    access.revoke(vault_dir, "KEY", "write")
    assert access.can_write(vault_dir, "KEY") is False
    access.clear_permissions(vault_dir, "KEY")
    assert access.can_write(vault_dir, "KEY") is True


def test_access_file_persists(vault_dir):
    access.revoke(vault_dir, "API_KEY", "write")
    # Re-read from disk
    perms = access.get_permissions(vault_dir, "API_KEY")
    assert "write" not in perms
    assert "read" in perms


def test_multiple_keys_independent(vault_dir):
    access.revoke(vault_dir, "KEY_A", "write")
    # KEY_B should still have default full access
    assert access.can_write(vault_dir, "KEY_B") is True
