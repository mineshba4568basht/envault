"""Sync module: import/export .env files to/from the vault."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Tuple

from envault.vault import Vault


_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value string."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return value


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse .env file content into a key/value dict, skipping comments."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _LINE_RE.match(stripped)
        if match:
            result[match.group("key")] = _strip_quotes(match.group("value"))
    return result


def import_dotenv(vault: Vault, dotenv_path: str | Path, overwrite: bool = True) -> Tuple[int, int]:
    """Read a .env file and store every variable into *vault*.

    Returns (imported_count, skipped_count).
    """
    path = Path(dotenv_path)
    text = path.read_text(encoding="utf-8")
    pairs = parse_dotenv(text)

    imported = 0
    skipped = 0
    for key, value in pairs.items():
        if not overwrite:
            try:
                vault.get(key)
                skipped += 1
                continue
            except KeyError:
                pass
        vault.set(key, value)
        imported += 1

    return imported, skipped


def sync_to_dotenv(vault: Vault, dotenv_path: str | Path, overwrite: bool = True) -> Tuple[int, int]:
    """Write all secrets from *vault* into a .env file.

    Returns (written_count, skipped_count).
    """
    from envault.export import export_dotenv  # avoid circular at module level

    path = Path(dotenv_path)
    secrets = vault.list()

    written = 0
    skipped = 0

    existing: Dict[str, str] = {}
    if path.exists() and not overwrite:
        existing = parse_dotenv(path.read_text(encoding="utf-8"))

    data = {key: vault.get(key) for key in secrets}
    if not overwrite:
        for key in list(data.keys()):
            if key in existing:
                del data[key]
                skipped += 1
            else:
                written += 1
    else:
        written = len(data)

    if data or overwrite:
        content = export_dotenv(data)
        path.write_text(content, encoding="utf-8")

    return written, skipped
