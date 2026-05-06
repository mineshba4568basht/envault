"""Tests for envault.sync (import_dotenv / sync_to_dotenv / parse_dotenv)."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.sync import import_dotenv, parse_dotenv, sync_to_dotenv
from envault.vault import Vault


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_vault(tmp_path: Path) -> Vault:
    return Vault(str(tmp_path / "vault"), password="test-password")


@pytest.fixture()
def dotenv_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "SECRET_KEY=\"my secret\"\n"
        "# a comment\n"
        "EMPTY=\n",
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# parse_dotenv
# ---------------------------------------------------------------------------

def test_parse_dotenv_basic(dotenv_file: Path) -> None:
    result = parse_dotenv(dotenv_file.read_text())
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_dotenv_strips_quotes(dotenv_file: Path) -> None:
    result = parse_dotenv(dotenv_file.read_text())
    assert result["SECRET_KEY"] == "my secret"


def test_parse_dotenv_ignores_comments(dotenv_file: Path) -> None:
    result = parse_dotenv(dotenv_file.read_text())
    assert not any(k.startswith("#") for k in result)


def test_parse_dotenv_empty_value(dotenv_file: Path) -> None:
    result = parse_dotenv(dotenv_file.read_text())
    assert result["EMPTY"] == ""


# ---------------------------------------------------------------------------
# import_dotenv
# ---------------------------------------------------------------------------

def test_import_dotenv_stores_all_keys(tmp_vault: Vault, dotenv_file: Path) -> None:
    imported, skipped = import_dotenv(tmp_vault, dotenv_file)
    assert imported == 4
    assert skipped == 0
    assert tmp_vault.get("DB_HOST") == "localhost"


def test_import_dotenv_no_overwrite_skips_existing(tmp_vault: Vault, dotenv_file: Path) -> None:
    tmp_vault.set("DB_HOST", "original")
    imported, skipped = import_dotenv(tmp_vault, dotenv_file, overwrite=False)
    assert skipped == 1
    assert tmp_vault.get("DB_HOST") == "original"


def test_import_dotenv_overwrite_replaces(tmp_vault: Vault, dotenv_file: Path) -> None:
    tmp_vault.set("DB_HOST", "original")
    import_dotenv(tmp_vault, dotenv_file, overwrite=True)
    assert tmp_vault.get("DB_HOST") == "localhost"


# ---------------------------------------------------------------------------
# sync_to_dotenv
# ---------------------------------------------------------------------------

def test_sync_to_dotenv_creates_file(tmp_vault: Vault, tmp_path: Path) -> None:
    tmp_vault.set("FOO", "bar")
    out = tmp_path / "out.env"
    written, skipped = sync_to_dotenv(tmp_vault, out)
    assert written == 1
    assert out.exists()
    assert "FOO=bar" in out.read_text()


def test_sync_to_dotenv_no_overwrite_skips(tmp_vault: Vault, tmp_path: Path) -> None:
    tmp_vault.set("FOO", "new")
    out = tmp_path / "out.env"
    out.write_text("FOO=old\n", encoding="utf-8")
    written, skipped = sync_to_dotenv(tmp_vault, out, overwrite=False)
    assert skipped == 1
    assert written == 0
