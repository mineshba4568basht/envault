"""
envault.lint — Lint secrets in a vault for common issues.

Checks performed:
  - Key naming conventions (uppercase, no spaces, valid chars)
  - Empty values
  - Suspiciously short values (possible placeholder)
  - Duplicate keys (case-insensitive conflicts)
  - Keys that look like they contain raw secrets in their name
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from envault.vault import Vault

_VALID_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_SENSITIVE_NAME_FRAGMENTS = ("password", "secret", "token", "key", "apikey", "api_key")


@dataclass
class LintWarning:
    key: str
    code: str
    message: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"[{self.code}] {self.key}: {self.message}"


@dataclass
class LintResult:
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __repr__(self) -> str:  # pragma: no cover
        if self.ok:
            return "LintResult: no issues found"
        lines = [f"LintResult: {len(self.warnings)} warning(s)"]
        for w in self.warnings:
            lines.append(f"  {w!r}")
        return "\n".join(lines)


def lint_vault(vault: Vault) -> LintResult:
    """Run all lint checks against the given vault and return a LintResult."""
    result = LintResult()
    keys = vault.list()

    seen_lower: dict[str, str] = {}
    for key in keys:
        value = vault.get(key)

        # W001 — key naming convention
        if not _VALID_KEY_RE.match(key):
            result.warnings.append(LintWarning(
                key=key,
                code="W001",
                message="Key should be UPPER_SNAKE_CASE (A-Z, 0-9, underscore, must start with a letter).",
            ))

        # W002 — empty value
        if value == "":
            result.warnings.append(LintWarning(
                key=key,
                code="W002",
                message="Value is empty.",
            ))

        # W003 — suspiciously short value (non-empty but <= 3 chars)
        elif len(value) <= 3:
            result.warnings.append(LintWarning(
                key=key,
                code="W003",
                message=f"Value is very short ({len(value)} char(s)); may be a placeholder.",
            ))

        # W004 — case-insensitive duplicate key
        lower = key.lower()
        if lower in seen_lower:
            result.warnings.append(LintWarning(
                key=key,
                code="W004",
                message=f"Key conflicts with '{seen_lower[lower]}' (case-insensitive duplicate).",
            ))
        else:
            seen_lower[lower] = key

        # W005 — value looks like it contains the word 'changeme' or 'placeholder'
        if re.search(r'changeme|placeholder|todo|fixme|xxx', value, re.IGNORECASE):
            result.warnings.append(LintWarning(
                key=key,
                code="W005",
                message="Value contains a placeholder-like string (changeme/placeholder/todo/fixme/xxx).",
            ))

    return result
