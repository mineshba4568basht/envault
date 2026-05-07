"""Tag management for vault secrets — allows grouping and filtering keys by tags."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

TAGS_FILENAME = ".tags.json"


def _tags_path(vault_dir: str) -> Path:
    return Path(vault_dir) / TAGS_FILENAME


def _load_tags(vault_dir: str) -> Dict[str, List[str]]:
    """Load the tags mapping {key: [tag, ...]} from disk."""
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_tags(vault_dir: str, data: Dict[str, List[str]]) -> None:
    """Persist the tags mapping to disk."""
    path = _tags_path(vault_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_tag(vault_dir: str, key: str, tag: str) -> None:
    """Add *tag* to *key*. Duplicate tags are silently ignored."""
    data = _load_tags(vault_dir)
    tags = data.setdefault(key, [])
    if tag not in tags:
        tags.append(tag)
    _save_tags(vault_dir, data)


def remove_tag(vault_dir: str, key: str, tag: str) -> bool:
    """Remove *tag* from *key*. Returns True if the tag existed."""
    data = _load_tags(vault_dir)
    tags = data.get(key, [])
    if tag not in tags:
        return False
    tags.remove(tag)
    if not tags:
        data.pop(key, None)
    else:
        data[key] = tags
    _save_tags(vault_dir, data)
    return True


def get_tags(vault_dir: str, key: str) -> List[str]:
    """Return the list of tags associated with *key*."""
    return _load_tags(vault_dir).get(key, [])


def keys_for_tag(vault_dir: str, tag: str) -> List[str]:
    """Return all keys that carry *tag*."""
    data = _load_tags(vault_dir)
    return [k for k, tags in data.items() if tag in tags]


def clear_tags(vault_dir: str, key: str) -> None:
    """Remove all tags for *key*."""
    data = _load_tags(vault_dir)
    data.pop(key, None)
    _save_tags(vault_dir, data)


def all_tags(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full tags mapping."""
    return _load_tags(vault_dir)
