"""Tests for envault.search module."""

import pytest

from envault.vault import Vault
from envault.search import grep_keys, search_keys, search_values


@pytest.fixture()
def vault(tmp_path):
    v = Vault(str(tmp_path / "vault"), password="test-pass")
    v.set("DATABASE_URL", "postgres://localhost/db")
    v.set("DATABASE_PASSWORD", "s3cr3t")
    v.set("REDIS_URL", "redis://localhost:6379")
    v.set("API_KEY", "abc123")
    v.set("api_secret", "xyz789")
    return v


# --- search_keys ---

def test_search_keys_wildcard_prefix(vault):
    results = search_keys(vault, "DATABASE_*")
    assert set(results) == {"DATABASE_URL", "DATABASE_PASSWORD"}


def test_search_keys_wildcard_suffix(vault):
    results = search_keys(vault, "*_URL")
    assert set(results) == {"DATABASE_URL", "REDIS_URL"}


def test_search_keys_no_match(vault):
    assert search_keys(vault, "NONEXISTENT_*") == []


def test_search_keys_case_insensitive_by_default(vault):
    results = search_keys(vault, "api_*")
    # matches both API_KEY and api_secret when case-insensitive
    assert "API_KEY" in results
    assert "api_secret" in results


def test_search_keys_case_sensitive(vault):
    results = search_keys(vault, "api_*", case_sensitive=True)
    assert results == ["api_secret"]


def test_search_keys_regex(vault):
    results = search_keys(vault, r"^(DATABASE|REDIS)_", use_regex=True)
    assert set(results) == {"DATABASE_URL", "DATABASE_PASSWORD", "REDIS_URL"}


def test_search_keys_regex_no_match(vault):
    assert search_keys(vault, r"^MISSING", use_regex=True) == []


# --- search_values ---

def test_search_values_wildcard(vault):
    results = search_values(vault, "*localhost*")
    assert "DATABASE_URL" in results
    assert "REDIS_URL" in results
    assert "API_KEY" not in results


def test_search_values_regex(vault):
    results = search_values(vault, r"^[a-z0-9]+$", use_regex=True, case_sensitive=True)
    # abc123 and xyz789 match; postgres/redis URLs do not
    assert "API_KEY" in results
    assert "api_secret" in results
    assert "DATABASE_URL" not in results


# --- grep_keys ---

def test_grep_keys_basic(vault):
    results = grep_keys(vault, "URL")
    assert set(results) == {"DATABASE_URL", "REDIS_URL"}


def test_grep_keys_case_insensitive(vault):
    results = grep_keys(vault, "api")
    assert "API_KEY" in results
    assert "api_secret" in results


def test_grep_keys_case_sensitive(vault):
    results = grep_keys(vault, "api", case_sensitive=True)
    assert results == ["api_secret"]


def test_grep_keys_no_match(vault):
    assert grep_keys(vault, "NOTHING") == []
