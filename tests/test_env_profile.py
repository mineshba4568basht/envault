"""Tests for envault.env_profile — named environment profile support."""

import pytest
from pathlib import Path

from envault.env_profile import (
    assign_key,
    unassign_key,
    list_profiles,
    get_profile_keys,
    get_key_profiles,
    delete_profile,
)


@pytest.fixture
def vault_dir(tmp_path: Path) -> str:
    return str(tmp_path / "vault")


def test_list_profiles_empty(vault_dir):
    assert list_profiles(vault_dir) == []


def test_assign_key_creates_profile(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assert "dev" in list_profiles(vault_dir)


def test_assign_key_adds_to_profile(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "dev", "API_KEY")
    keys = get_profile_keys(vault_dir, "dev")
    assert "DB_URL" in keys
    assert "API_KEY" in keys


def test_assign_key_idempotent(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "dev", "DB_URL")
    assert get_profile_keys(vault_dir, "dev").count("DB_URL") == 1


def test_get_profile_keys_unknown_profile_returns_empty(vault_dir):
    assert get_profile_keys(vault_dir, "nonexistent") == []


def test_multiple_profiles_independent(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "prod", "DB_URL")
    assign_key(vault_dir, "prod", "SECRET_KEY")
    assert get_profile_keys(vault_dir, "dev") == ["DB_URL"]
    assert set(get_profile_keys(vault_dir, "prod")) == {"DB_URL", "SECRET_KEY"}


def test_get_key_profiles_returns_all_containing_profiles(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "staging", "DB_URL")
    assign_key(vault_dir, "prod", "OTHER")
    profiles = get_key_profiles(vault_dir, "DB_URL")
    assert set(profiles) == {"dev", "staging"}


def test_get_key_profiles_not_found_returns_empty(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assert get_key_profiles(vault_dir, "MISSING") == []


def test_unassign_key_removes_key(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "dev", "API_KEY")
    result = unassign_key(vault_dir, "dev", "DB_URL")
    assert result is True
    assert "DB_URL" not in get_profile_keys(vault_dir, "dev")
    assert "API_KEY" in get_profile_keys(vault_dir, "dev")


def test_unassign_last_key_removes_profile(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    unassign_key(vault_dir, "dev", "DB_URL")
    assert "dev" not in list_profiles(vault_dir)


def test_unassign_missing_key_returns_false(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    result = unassign_key(vault_dir, "dev", "GHOST")
    assert result is False


def test_delete_profile_removes_it(vault_dir):
    assign_key(vault_dir, "dev", "DB_URL")
    assign_key(vault_dir, "prod", "DB_URL")
    result = delete_profile(vault_dir, "dev")
    assert result is True
    assert "dev" not in list_profiles(vault_dir)
    assert "prod" in list_profiles(vault_dir)


def test_delete_nonexistent_profile_returns_false(vault_dir):
    assert delete_profile(vault_dir, "ghost") is False
