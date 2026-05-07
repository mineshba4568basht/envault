"""Tests for envault.tags — tag management for vault secrets."""

import pytest

from envault.tags import (
    add_tag,
    all_tags,
    clear_tags,
    get_tags,
    keys_for_tag,
    remove_tag,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# add_tag / get_tags
# ---------------------------------------------------------------------------

def test_get_tags_returns_empty_for_unknown_key(vault_dir):
    assert get_tags(vault_dir, "MY_KEY") == []


def test_add_tag_single(vault_dir):
    add_tag(vault_dir, "DB_URL", "database")
    assert get_tags(vault_dir, "DB_URL") == ["database"]


def test_add_tag_multiple(vault_dir):
    add_tag(vault_dir, "API_KEY", "api")
    add_tag(vault_dir, "API_KEY", "production")
    assert set(get_tags(vault_dir, "API_KEY")) == {"api", "production"}


def test_add_tag_duplicate_is_idempotent(vault_dir):
    add_tag(vault_dir, "TOKEN", "auth")
    add_tag(vault_dir, "TOKEN", "auth")
    assert get_tags(vault_dir, "TOKEN") == ["auth"]


# ---------------------------------------------------------------------------
# remove_tag
# ---------------------------------------------------------------------------

def test_remove_tag_returns_true_when_present(vault_dir):
    add_tag(vault_dir, "SECRET", "internal")
    assert remove_tag(vault_dir, "SECRET", "internal") is True
    assert get_tags(vault_dir, "SECRET") == []


def test_remove_tag_returns_false_when_absent(vault_dir):
    assert remove_tag(vault_dir, "MISSING", "nope") is False


def test_remove_tag_cleans_up_empty_key(vault_dir):
    add_tag(vault_dir, "KEY", "only")
    remove_tag(vault_dir, "KEY", "only")
    assert "KEY" not in all_tags(vault_dir)


# ---------------------------------------------------------------------------
# keys_for_tag
# ---------------------------------------------------------------------------

def test_keys_for_tag_returns_matching_keys(vault_dir):
    add_tag(vault_dir, "DB_PASS", "database")
    add_tag(vault_dir, "DB_USER", "database")
    add_tag(vault_dir, "API_KEY", "api")
    result = keys_for_tag(vault_dir, "database")
    assert set(result) == {"DB_PASS", "DB_USER"}


def test_keys_for_tag_returns_empty_when_no_match(vault_dir):
    add_tag(vault_dir, "FOO", "bar")
    assert keys_for_tag(vault_dir, "nonexistent") == []


# ---------------------------------------------------------------------------
# clear_tags
# ---------------------------------------------------------------------------

def test_clear_tags_removes_all_tags_for_key(vault_dir):
    add_tag(vault_dir, "KEY", "a")
    add_tag(vault_dir, "KEY", "b")
    clear_tags(vault_dir, "KEY")
    assert get_tags(vault_dir, "KEY") == []


def test_clear_tags_does_not_affect_other_keys(vault_dir):
    add_tag(vault_dir, "KEY_A", "shared")
    add_tag(vault_dir, "KEY_B", "shared")
    clear_tags(vault_dir, "KEY_A")
    assert get_tags(vault_dir, "KEY_B") == ["shared"]


# ---------------------------------------------------------------------------
# all_tags
# ---------------------------------------------------------------------------

def test_all_tags_returns_full_mapping(vault_dir):
    add_tag(vault_dir, "X", "t1")
    add_tag(vault_dir, "Y", "t2")
    mapping = all_tags(vault_dir)
    assert mapping["X"] == ["t1"]
    assert mapping["Y"] == ["t2"]


def test_all_tags_empty_when_no_tags(vault_dir):
    assert all_tags(vault_dir) == {}
