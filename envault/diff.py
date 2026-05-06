"""Diff utilities for comparing vault secrets against a .env file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from envault.sync import parse_dotenv
from envault.vault import Vault


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    vault_value: str | None = None
    file_value: str | None = None

    def __repr__(self) -> str:
        if self.status == "added":
            return f"+ {self.key}  (in vault, not in file)"
        if self.status == "removed":
            return f"- {self.key}  (in file, not in vault)"
        if self.status == "changed":
            return f"~ {self.key}  (values differ)"
        return f"  {self.key}  (unchanged)"


def diff_vault_vs_file(
    vault: Vault,
    dotenv_path: str,
    *,
    include_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare vault secrets against a .env file.

    Returns a list of DiffEntry objects describing the differences.
    """
    with open(dotenv_path, "r", encoding="utf-8") as fh:
        file_secrets: Dict[str, str] = parse_dotenv(fh.read())

    vault_keys = set(vault.list())
    file_keys = set(file_secrets.keys())
    all_keys = vault_keys | file_keys

    entries: List[DiffEntry] = []
    for key in sorted(all_keys):
        in_vault = key in vault_keys
        in_file = key in file_keys

        if in_vault and not in_file:
            entries.append(DiffEntry(key=key, status="added", vault_value=vault.get(key)))
        elif in_file and not in_vault:
            entries.append(
                DiffEntry(key=key, status="removed", file_value=file_secrets[key])
            )
        else:
            vault_val = vault.get(key)
            file_val = file_secrets[key]
            if vault_val != file_val:
                entries.append(
                    DiffEntry(
                        key=key,
                        status="changed",
                        vault_value=vault_val,
                        file_value=file_val,
                    )
                )
            elif include_unchanged:
                entries.append(
                    DiffEntry(
                        key=key,
                        status="unchanged",
                        vault_value=vault_val,
                        file_value=file_val,
                    )
                )

    return entries


def format_diff(entries: List[DiffEntry]) -> str:
    """Return a human-readable diff summary."""
    if not entries:
        return "No differences found."
    return "\n".join(repr(e) for e in entries)
