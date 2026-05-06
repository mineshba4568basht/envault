"""Search and filter secrets within a vault."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional

from envault.vault import Vault


def search_keys(
    vault: Vault,
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> List[str]:
    """Return vault keys matching *pattern*.

    By default uses shell-style wildcards (fnmatch).  Pass
    ``use_regex=True`` to treat *pattern* as a regular expression.
    Matching is case-insensitive unless *case_sensitive* is True.
    """
    all_keys: List[str] = vault.list_keys()

    flags = 0 if case_sensitive else re.IGNORECASE

    if use_regex:
        compiled = re.compile(pattern, flags)
        return [k for k in all_keys if compiled.search(k)]

    if not case_sensitive:
        return [
            k for k in all_keys
            if fnmatch.fnmatchcase(k.lower(), pattern.lower())
        ]
    return [k for k in all_keys if fnmatch.fnmatchcase(k, pattern)]


def search_values(
    vault: Vault,
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return a mapping of key → value for secrets whose *value* matches."""
    all_keys: List[str] = vault.list_keys()
    flags = 0 if case_sensitive else re.IGNORECASE

    results: Dict[str, str] = {}
    for key in all_keys:
        value: Optional[str] = vault.get(key)
        if value is None:
            continue
        if use_regex:
            if re.search(pattern, value, flags):
                results[key] = value
        else:
            needle = pattern if case_sensitive else pattern.lower()
            haystack = value if case_sensitive else value.lower()
            if fnmatch.fnmatchcase(haystack, needle):
                results[key] = value
    return results


def grep_keys(vault: Vault, substring: str, *, case_sensitive: bool = False) -> List[str]:
    """Return keys that contain *substring* (simple contains check)."""
    all_keys: List[str] = vault.list_keys()
    needle = substring if case_sensitive else substring.lower()
    return [
        k for k in all_keys
        if needle in (k if case_sensitive else k.lower())
    ]
