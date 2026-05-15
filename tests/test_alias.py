"""Tests for envault.alias."""

from __future__ import annotations

import pytest

from envault.alias import (
    list_aliases,
    remove_alias,
    resolve,
    reverse_lookup,
    set_alias,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_list_aliases_empty(vault_dir):
    assert list_aliases(vault_dir) == {}


def test_set_alias_creates_mapping(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert list_aliases(vault_dir) == {"db": "DATABASE_URL"}


def test_set_alias_multiple(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    set_alias(vault_dir, "sk", "SECRET_KEY")
    aliases = list_aliases(vault_dir)
    assert aliases["db"] == "DATABASE_URL"
    assert aliases["sk"] == "SECRET_KEY"


def test_set_alias_overwrites_existing(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    set_alias(vault_dir, "db", "POSTGRES_DSN")
    assert list_aliases(vault_dir)["db"] == "POSTGRES_DSN"


def test_remove_alias(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    remove_alias(vault_dir, "db")
    assert "db" not in list_aliases(vault_dir)


def test_remove_alias_unknown_is_silent(vault_dir):
    remove_alias(vault_dir, "nonexistent")  # should not raise


def test_resolve_known_alias(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert resolve(vault_dir, "db") == "DATABASE_URL"


def test_resolve_unknown_returns_input(vault_dir):
    assert resolve(vault_dir, "DATABASE_URL") == "DATABASE_URL"


def test_reverse_lookup_single(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert reverse_lookup(vault_dir, "DATABASE_URL") == ["db"]


def test_reverse_lookup_multiple(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    set_alias(vault_dir, "database", "DATABASE_URL")
    hits = reverse_lookup(vault_dir, "DATABASE_URL")
    assert sorted(hits) == ["database", "db"]


def test_reverse_lookup_no_match(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    assert reverse_lookup(vault_dir, "SECRET_KEY") == []


def test_list_aliases_returns_copy(vault_dir):
    set_alias(vault_dir, "db", "DATABASE_URL")
    aliases = list_aliases(vault_dir)
    aliases["db"] = "MUTATED"
    # original on disk should be unchanged
    assert list_aliases(vault_dir)["db"] == "DATABASE_URL"
