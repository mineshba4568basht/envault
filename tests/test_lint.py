import pytest
from envault.vault import Vault
from envault.lint import lint_vault, LintWarning, LintResult


@pytest.fixture
def tmp_vault(tmp_path):
    return Vault(vault_dir=str(tmp_path), password="testpass")


# ── LintResult helpers ───────────────────────────────────────────────────────

def test_lint_result_ok_when_no_warnings():
    result = LintResult()
    assert result.ok is True


def test_lint_result_not_ok_when_warnings():
    result = LintResult(warnings=[LintWarning(key="X", code="W001", message="test")])
    assert result.ok is False


# ── W001: key naming convention ───────────────────────────────────────────────

def test_valid_key_no_warning(tmp_vault):
    tmp_vault.set("MY_KEY", "somevalue")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W001" not in codes


def test_lowercase_key_triggers_w001(tmp_vault):
    tmp_vault.set("my_key", "somevalue")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W001" in codes


def test_key_with_space_triggers_w001(tmp_vault):
    tmp_vault.set("MY KEY", "somevalue")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W001" in codes


def test_key_starting_with_digit_triggers_w001(tmp_vault):
    tmp_vault.set("1KEY", "somevalue")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W001" in codes


# ── W002: empty value ─────────────────────────────────────────────────────────

def test_empty_value_triggers_w002(tmp_vault):
    tmp_vault.set("EMPTY_VAL", "")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W002" in codes


def test_nonempty_value_no_w002(tmp_vault):
    tmp_vault.set("GOOD_VAL", "hello")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W002" not in codes


# ── W003: suspiciously short value ────────────────────────────────────────────

def test_short_value_triggers_w003(tmp_vault):
    tmp_vault.set("SHORT_VAL", "ab")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W003" in codes


def test_value_of_four_chars_no_w003(tmp_vault):
    tmp_vault.set("FINE_VAL", "abcd")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W003" not in codes


# ── W004: case-insensitive duplicate ──────────────────────────────────────────

def test_case_insensitive_duplicate_triggers_w004(tmp_vault):
    tmp_vault.set("DB_HOST", "localhost")
    tmp_vault.set("db_host", "127.0.0.1")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W004" in codes


def test_unique_keys_no_w004(tmp_vault):
    tmp_vault.set("DB_HOST", "localhost")
    tmp_vault.set("DB_PORT", "5432")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W004" not in codes


# ── W005: placeholder value ───────────────────────────────────────────────────

def test_changeme_triggers_w005(tmp_vault):
    tmp_vault.set("API_KEY", "changeme")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W005" in codes


def test_placeholder_triggers_w005(tmp_vault):
    tmp_vault.set("SECRET_KEY", "placeholder_value")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W005" in codes


def test_real_value_no_w005(tmp_vault):
    tmp_vault.set("API_KEY", "sk-abc123realtoken")
    result = lint_vault(tmp_vault)
    codes = [w.code for w in result.warnings]
    assert "W005" not in codes


# ── empty vault ───────────────────────────────────────────────────────────────

def test_empty_vault_is_ok(tmp_vault):
    result = lint_vault(tmp_vault)
    assert result.ok is True
    assert result.warnings == []
