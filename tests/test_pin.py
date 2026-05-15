"""Tests for envault.pin module."""

import pytest

from envault.pin import (
    PinnedKeyError,
    clear_pins,
    is_pinned,
    list_pinned,
    pin,
    unpin,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_is_pinned_default_false(vault_dir):
    assert is_pinned(vault_dir, "MY_KEY") is False


def test_pin_sets_key(vault_dir):
    pin(vault_dir, "MY_KEY")
    assert is_pinned(vault_dir, "MY_KEY") is True


def test_pin_does_not_affect_other_keys(vault_dir):
    pin(vault_dir, "KEY_A")
    assert is_pinned(vault_dir, "KEY_B") is False


def test_unpin_removes_key(vault_dir):
    pin(vault_dir, "MY_KEY")
    unpin(vault_dir, "MY_KEY")
    assert is_pinned(vault_dir, "MY_KEY") is False


def test_unpin_nonexistent_key_does_not_raise(vault_dir):
    unpin(vault_dir, "GHOST_KEY")  # should not raise


def test_list_pinned_empty(vault_dir):
    assert list_pinned(vault_dir) == []


def test_list_pinned_multiple(vault_dir):
    pin(vault_dir, "ZEBRA")
    pin(vault_dir, "ALPHA")
    pin(vault_dir, "MIDDLE")
    result = list_pinned(vault_dir)
    assert result == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_list_pinned_excludes_unpinned(vault_dir):
    pin(vault_dir, "KEY_A")
    pin(vault_dir, "KEY_B")
    unpin(vault_dir, "KEY_A")
    assert list_pinned(vault_dir) == ["KEY_B"]


def test_clear_pins_removes_all(vault_dir):
    pin(vault_dir, "KEY_A")
    pin(vault_dir, "KEY_B")
    clear_pins(vault_dir)
    assert list_pinned(vault_dir) == []


def test_pin_is_idempotent(vault_dir):
    pin(vault_dir, "MY_KEY")
    pin(vault_dir, "MY_KEY")
    assert is_pinned(vault_dir, "MY_KEY") is True
    assert list_pinned(vault_dir) == ["MY_KEY"]


def test_pinned_key_error_message():
    err = PinnedKeyError("SECRET_TOKEN")
    assert "SECRET_TOKEN" in str(err)
    assert err.key == "SECRET_TOKEN"


def test_pins_persisted_across_calls(vault_dir):
    pin(vault_dir, "PERSISTENT")
    # Simulate a fresh read by calling is_pinned independently
    assert is_pinned(vault_dir, "PERSISTENT") is True
    assert "PERSISTENT" in list_pinned(vault_dir)
