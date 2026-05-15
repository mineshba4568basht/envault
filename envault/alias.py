"""Key aliasing — map short alias names to full secret keys."""

from __future__ import annotations

import json
from pathlib import Path


def _alias_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".aliases.json"


def _load_aliases(vault_dir: str) -> dict[str, str]:
    p = _alias_path(vault_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_aliases(vault_dir: str, aliases: dict[str, str]) -> None:
    p = _alias_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(aliases, f, indent=2)


def set_alias(vault_dir: str, alias: str, key: str) -> None:
    """Map *alias* to the real secret *key*."""
    aliases = _load_aliases(vault_dir)
    aliases[alias] = key
    _save_aliases(vault_dir, aliases)


def remove_alias(vault_dir: str, alias: str) -> None:
    """Remove an alias.  Silently ignores unknown aliases."""
    aliases = _load_aliases(vault_dir)
    aliases.pop(alias, None)
    _save_aliases(vault_dir, aliases)


def resolve(vault_dir: str, alias_or_key: str) -> str:
    """Return the real key for *alias_or_key*, or the value itself if not aliased."""
    aliases = _load_aliases(vault_dir)
    return aliases.get(alias_or_key, alias_or_key)


def list_aliases(vault_dir: str) -> dict[str, str]:
    """Return a copy of all alias → key mappings."""
    return dict(_load_aliases(vault_dir))


def reverse_lookup(vault_dir: str, key: str) -> list[str]:
    """Return all aliases that point to *key*."""
    aliases = _load_aliases(vault_dir)
    return [alias for alias, target in aliases.items() if target == key]
