"""Tests for envault.diff module."""

import os
import pytest

from envault.vault import Vault
from envault.diff import diff_vault_vs_file, format_diff, DiffEntry


@pytest.fixture
def tmp_vault(tmp_path):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    v = Vault(str(vault_dir), password="testpass")
    return v


@pytest.fixture
def dotenv_file(tmp_path):
    path = tmp_path / ".env"

    def _write(content: str) -> str:
        path.write_text(content, encoding="utf-8")
        return str(path)

    return _write


def test_diff_added_key(tmp_vault, dotenv_file):
    """Key in vault but not in file should be 'added'."""
    tmp_vault.set("SECRET", "abc123")
    path = dotenv_file("OTHER=value\n")
    entries = diff_vault_vs_file(tmp_vault, path)
    statuses = {e.key: e.status for e in entries}
    assert statuses["SECRET"] == "added"


def test_diff_removed_key(tmp_vault, dotenv_file):
    """Key in file but not in vault should be 'removed'."""
    path = dotenv_file("MISSING=value\n")
    entries = diff_vault_vs_file(tmp_vault, path)
    statuses = {e.key: e.status for e in entries}
    assert statuses["MISSING"] == "removed"


def test_diff_changed_key(tmp_vault, dotenv_file):
    """Key present in both but with different values should be 'changed'."""
    tmp_vault.set("DB_URL", "postgres://new")
    path = dotenv_file("DB_URL=postgres://old\n")
    entries = diff_vault_vs_file(tmp_vault, path)
    statuses = {e.key: e.status for e in entries}
    assert statuses["DB_URL"] == "changed"


def test_diff_unchanged_key_excluded_by_default(tmp_vault, dotenv_file):
    """Unchanged keys should not appear unless include_unchanged=True."""
    tmp_vault.set("KEY", "same")
    path = dotenv_file("KEY=same\n")
    entries = diff_vault_vs_file(tmp_vault, path)
    assert all(e.status != "unchanged" for e in entries)


def test_diff_unchanged_key_included(tmp_vault, dotenv_file):
    """Unchanged keys appear when include_unchanged=True."""
    tmp_vault.set("KEY", "same")
    path = dotenv_file("KEY=same\n")
    entries = diff_vault_vs_file(tmp_vault, path, include_unchanged=True)
    statuses = {e.key: e.status for e in entries}
    assert statuses["KEY"] == "unchanged"


def test_diff_empty_vault_and_file(tmp_vault, dotenv_file):
    """No differences when both vault and file are empty."""
    path = dotenv_file("")
    entries = diff_vault_vs_file(tmp_vault, path)
    assert entries == []


def test_format_diff_no_differences():
    assert format_diff([]) == "No differences found."


def test_format_diff_shows_all_statuses():
    entries = [
        DiffEntry(key="A", status="added", vault_value="1"),
        DiffEntry(key="B", status="removed", file_value="2"),
        DiffEntry(key="C", status="changed", vault_value="x", file_value="y"),
    ]
    output = format_diff(entries)
    assert "+ A" in output
    assert "- B" in output
    assert "~ C" in output


def test_diff_entry_repr_added():
    e = DiffEntry(key="FOO", status="added", vault_value="bar")
    assert repr(e).startswith("+")


def test_diff_entry_repr_removed():
    e = DiffEntry(key="FOO", status="removed", file_value="bar")
    assert repr(e).startswith("-")
