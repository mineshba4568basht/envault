"""Tests for vault bundle export/import (envault.share)."""

import pytest
from pathlib import Path
from envault.vault import Vault
from envault.share import export_bundle, import_bundle, import_bundle_from_file


PASSWORD = "test-password"


@pytest.fixture
def tmp_vault(tmp_path):
    vault = Vault(str(tmp_path / "vault"), PASSWORD)
    vault.set("KEY1", "value1")
    vault.set("KEY2", "value2")
    return vault


@pytest.fixture
def empty_vault(tmp_path):
    return Vault(str(tmp_path / "empty_vault"), PASSWORD)


def test_export_bundle_returns_string(tmp_vault):
    bundle = export_bundle(tmp_vault, PASSWORD)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_bundle_writes_file(tmp_vault, tmp_path):
    out = str(tmp_path / "bundle.enc")
    export_bundle(tmp_vault, PASSWORD, output_path=out)
    assert Path(out).exists()
    assert len(Path(out).read_text()) > 0


def test_import_bundle_roundtrip(tmp_vault, empty_vault):
    bundle = export_bundle(tmp_vault, PASSWORD)
    count = import_bundle(bundle, PASSWORD, empty_vault)
    assert count == 2
    assert empty_vault.get("KEY1") == "value1"
    assert empty_vault.get("KEY2") == "value2"


def test_import_bundle_wrong_password_raises(tmp_vault, empty_vault):
    bundle = export_bundle(tmp_vault, PASSWORD)
    with pytest.raises(Exception):
        import_bundle(bundle, "wrong-password", empty_vault)


def test_import_bundle_no_overwrite_skips_existing(tmp_vault, tmp_path):
    dest_vault = Vault(str(tmp_path / "dest"), PASSWORD)
    dest_vault.set("KEY1", "original")
    bundle = export_bundle(tmp_vault, PASSWORD)
    count = import_bundle(bundle, PASSWORD, dest_vault, overwrite=False)
    assert count == 1  # only KEY2 imported
    assert dest_vault.get("KEY1") == "original"


def test_import_bundle_overwrite_replaces_existing(tmp_vault, tmp_path):
    dest_vault = Vault(str(tmp_path / "dest2"), PASSWORD)
    dest_vault.set("KEY1", "original")
    bundle = export_bundle(tmp_vault, PASSWORD)
    count = import_bundle(bundle, PASSWORD, dest_vault, overwrite=True)
    assert count == 2
    assert dest_vault.get("KEY1") == "value1"


def test_import_bundle_from_file(tmp_vault, empty_vault, tmp_path):
    out = str(tmp_path / "bundle.enc")
    export_bundle(tmp_vault, PASSWORD, output_path=out)
    count = import_bundle_from_file(out, PASSWORD, empty_vault)
    assert count == 2


def test_export_empty_vault_imports_zero(empty_vault, tmp_path):
    dest = Vault(str(tmp_path / "dest3"), PASSWORD)
    bundle = export_bundle(empty_vault, PASSWORD)
    count = import_bundle(bundle, PASSWORD, dest)
    assert count == 0
