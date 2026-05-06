"""Tests for envault.export module."""

import json
import pytest

from envault.export import export_secrets, export_dotenv, export_json, export_shell


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PASS": "s3cr3t",
    "API_KEY": "key with spaces",
    "QUOTE_VAL": 'say "hello"',
}


def test_export_dotenv_simple():
    result = export_dotenv({"FOO": "bar", "BAZ": "qux"})
    assert "BAZ=qux" in result
    assert "FOO=bar" in result


def test_export_dotenv_quotes_values_with_spaces():
    result = export_dotenv({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_export_dotenv_escapes_double_quotes():
    result = export_dotenv({"V": 'say "hi"'})
    assert '\\"' in result


def test_export_dotenv_ends_with_newline():
    result = export_dotenv({"K": "v"})
    assert result.endswith("\n")


def test_export_dotenv_empty():
    assert export_dotenv({}) == ""


def test_export_json_valid():
    result = export_json({"A": "1", "B": "2"})
    parsed = json.loads(result)
    assert parsed == {"A": "1", "B": "2"}


def test_export_json_sorted_keys():
    result = export_json({"Z": "last", "A": "first"})
    keys = list(json.loads(result).keys())
    assert keys == sorted(keys)


def test_export_shell_format():
    result = export_shell({"TOKEN": "abc123"})
    assert "export TOKEN='abc123'" in result


def test_export_shell_escapes_single_quotes():
    result = export_shell({"V": "it's here"})
    assert "export V='it'\"'\"'s here'" in result


def test_export_secrets_dispatches_dotenv():
    result = export_secrets({"X": "y"}, "dotenv")
    assert "X=y" in result


def test_export_secrets_dispatches_json():
    result = export_secrets({"X": "y"}, "json")
    assert json.loads(result) == {"X": "y"}


def test_export_secrets_dispatches_shell():
    result = export_secrets({"X": "y"}, "shell")
    assert "export X='y'" in result


def test_export_secrets_invalid_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_secrets({"K": "v"}, "yaml")
