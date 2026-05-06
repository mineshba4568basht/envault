"""Tests for envault.rotate key-rotation helpers."""

from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.rotate import rotate_key, rotate_key_for_all_vaults


OLD_PASS = "old-secret-pass"
NEW_PASS = "new-secret-pass"


@pytest.fixture()
def vault_with_secrets(tmp_path):
    """Return a populated Vault and its directory."""
    v = Vault(tmp_path, OLD_PASS, vault_name="default")
    v.set("API_KEY", "abc123")
    v.set("DB_URL", "postgres://localhost/mydb")
    v.set("SECRET_TOKEN", "t0p$ecret")
    return tmp_path, v


def test_rotate_key_returns_secret_count(vault_with_secrets):
    vault_dir, _ = vault_with_secrets
    count = rotate_key(vault_dir, OLD_PASS, NEW_PASS)
    assert count == 3


def test_rotated_secrets_readable_with_new_password(vault_with_secrets):
    vault_dir, _ = vault_with_secrets
    rotate_key(vault_dir, OLD_PASS, NEW_PASS)

    new_vault = Vault(vault_dir, NEW_PASS, vault_name="default")
    assert new_vault.get("API_KEY") == "abc123"
    assert new_vault.get("DB_URL") == "postgres://localhost/mydb"
    assert new_vault.get("SECRET_TOKEN") == "t0p$ecret"


def test_rotated_secrets_not_readable_with_old_password(vault_with_secrets):
    vault_dir, _ = vault_with_secrets
    rotate_key(vault_dir, OLD_PASS, NEW_PASS)

    old_vault = Vault(vault_dir, OLD_PASS, vault_name="default")
    with pytest.raises(Exception):
        old_vault.get("API_KEY")


def test_rotate_key_wrong_old_password_raises(vault_with_secrets):
    vault_dir, _ = vault_with_secrets
    with pytest.raises(Exception):
        rotate_key(vault_dir, "wrong-password", NEW_PASS)


def test_rotate_key_empty_vault_returns_zero(tmp_path):
    # Create an empty vault file so storage exists but has no secrets.
    Vault(tmp_path, OLD_PASS, vault_name="empty")
    count = rotate_key(tmp_path, OLD_PASS, NEW_PASS, vault_name="empty")
    assert count == 0


def test_rotate_key_for_all_vaults(tmp_path):
    for name in ("alpha", "beta"):
        v = Vault(tmp_path, OLD_PASS, vault_name=name)
        v.set("KEY", f"value-{name}")

    results = rotate_key_for_all_vaults(tmp_path, OLD_PASS, NEW_PASS)

    assert results == {"alpha": 1, "beta": 1}

    for name in ("alpha", "beta"):
        v = Vault(tmp_path, NEW_PASS, vault_name=name)
        assert v.get("KEY") == f"value-{name}"


def test_rotate_writes_audit_entry(vault_with_secrets):
    from envault.audit import read

    vault_dir, _ = vault_with_secrets
    rotate_key(vault_dir, OLD_PASS, NEW_PASS)

    entries = read(vault_dir)
    assert any(e.get("action") == "rotate_key" for e in entries)
