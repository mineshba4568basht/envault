"""Tests for envault.template — placeholder rendering against a Vault."""

import pytest

from envault.vault import Vault
from envault.template import (
    render_string,
    render_file,
    TemplateMissingKeyError,
)

PASSWORD = "test-password"


@pytest.fixture()
def tmp_vault(tmp_path):
    v = Vault(str(tmp_path / "vault"), PASSWORD)
    v.set("DB_HOST", "localhost")
    v.set("DB_PORT", "5432")
    v.set("API_KEY", "s3cr3t")
    return v


# ---------------------------------------------------------------------------
# render_string
# ---------------------------------------------------------------------------

def test_render_string_single_placeholder(tmp_vault):
    result = render_string("host={{ DB_HOST }}", tmp_vault)
    assert result == "host=localhost"


def test_render_string_multiple_placeholders(tmp_vault):
    tmpl = "{{DB_HOST}}:{{DB_PORT}}"
    assert render_string(tmpl, tmp_vault) == "localhost:5432"


def test_render_string_no_placeholders(tmp_vault):
    tmpl = "nothing to replace here"
    assert render_string(tmpl, tmp_vault) == tmpl


def test_render_string_whitespace_variants(tmp_vault):
    """Both {{ KEY }} and {{KEY}} and {{  KEY  }} should work."""
    assert render_string("{{  API_KEY  }}", tmp_vault) == "s3cr3t"
    assert render_string("{{ API_KEY }}", tmp_vault) == "s3cr3t"
    assert render_string("{{API_KEY}}", tmp_vault) == "s3cr3t"


def test_render_string_strict_raises_on_missing(tmp_vault):
    with pytest.raises(TemplateMissingKeyError) as exc_info:
        render_string("{{ MISSING_KEY }}", tmp_vault, strict=True)
    assert exc_info.value.key == "MISSING_KEY"


def test_render_string_non_strict_keeps_placeholder(tmp_vault):
    result = render_string("{{ MISSING_KEY }}", tmp_vault, strict=False)
    assert result == "{{ MISSING_KEY }}"


def test_render_string_non_strict_with_default(tmp_vault):
    result = render_string("{{ MISSING_KEY }}", tmp_vault, strict=False, default="")
    assert result == ""


def test_template_missing_key_error_message():
    err = TemplateMissingKeyError("FOO")
    assert "FOO" in str(err)


# ---------------------------------------------------------------------------
# render_file
# ---------------------------------------------------------------------------

def test_render_file_writes_output(tmp_vault, tmp_path):
    src = tmp_path / "config.tmpl"
    dst = tmp_path / "config.env"
    src.write_text("HOST={{ DB_HOST }}\nPORT={{ DB_PORT }}\n")

    count = render_file(str(src), str(dst), tmp_vault)

    assert count == 2
    output = dst.read_text()
    assert output == "HOST=localhost\nPORT=5432\n"


def test_render_file_returns_substitution_count(tmp_vault, tmp_path):
    src = tmp_path / "t.tmpl"
    dst = tmp_path / "t.out"
    src.write_text("no placeholders here")
    count = render_file(str(src), str(dst), tmp_vault)
    assert count == 0


def test_render_file_strict_raises_for_missing(tmp_vault, tmp_path):
    src = tmp_path / "bad.tmpl"
    dst = tmp_path / "bad.out"
    src.write_text("value={{ NOPE }}")
    with pytest.raises(TemplateMissingKeyError):
        render_file(str(src), str(dst), tmp_vault, strict=True)
