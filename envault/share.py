"""Vault sharing: export and import encrypted vault bundles for sharing across environments."""

import json
import base64
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt
from envault.vault import Vault


BUNDLE_VERSION = 1


def export_bundle(vault: Vault, password: str, output_path: Optional[str] = None) -> str:
    """Export all secrets from a vault as an encrypted portable bundle (base64-encoded JSON).

    Returns the bundle string and optionally writes it to output_path.
    """
    secrets = vault.list()
    plaintext_data = {key: vault.get(key) for key in secrets}
    payload = json.dumps({"version": BUNDLE_VERSION, "secrets": plaintext_data}).encode()
    encrypted = encrypt(password, payload)
    bundle = base64.b64encode(encrypted).decode()

    if output_path:
        Path(output_path).write_text(bundle)

    return bundle


def import_bundle(bundle_str: str, password: str, vault: Vault, overwrite: bool = False) -> int:
    """Import secrets from an encrypted bundle string into a vault.

    Returns the number of secrets imported.
    Raises ValueError if the bundle version is unsupported or data is malformed.
    """
    raw = base64.b64decode(bundle_str.strip())
    decrypted = decrypt(password, raw)
    data = json.loads(decrypted.decode())

    if data.get("version") != BUNDLE_VERSION:
        raise ValueError(f"Unsupported bundle version: {data.get('version')}")

    secrets = data.get("secrets", {})
    imported = 0
    for key, value in secrets.items():
        if not overwrite and key in vault.list():
            continue
        vault.set(key, value)
        imported += 1

    return imported


def import_bundle_from_file(file_path: str, password: str, vault: Vault, overwrite: bool = False) -> int:
    """Read a bundle from a file and import it into the vault."""
    bundle_str = Path(file_path).read_text().strip()
    return import_bundle(bundle_str, password, vault, overwrite=overwrite)
