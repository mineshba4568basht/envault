"""Policy enforcement for vault secrets — define and validate rules like
required keys, forbidden patterns, and minimum secret lengths."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PolicyViolation:
    key: str
    rule: str
    message: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"PolicyViolation(key={self.key!r}, rule={self.rule!r}, message={self.message!r})"


@dataclass
class PolicyResult:
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"PolicyResult(ok={self.ok}, violations={len(self.violations)})"


def check_policy(
    secrets: dict[str, str],
    required_keys: Optional[List[str]] = None,
    forbidden_pattern: Optional[str] = None,
    min_length: int = 0,
    key_pattern: Optional[str] = None,
) -> PolicyResult:
    """Validate *secrets* against the supplied policy rules.

    Args:
        secrets: mapping of key → plaintext value.
        required_keys: keys that must be present in the vault.
        forbidden_pattern: regex; values matching it are rejected.
        min_length: minimum character length for every value.
        key_pattern: regex that every key must match (e.g. ``^[A-Z_]+$``).

    Returns:
        A :class:`PolicyResult` whose ``ok`` attribute is ``True`` when no
        violations were found.
    """
    violations: List[PolicyViolation] = []

    for key in required_keys or []:
        if key not in secrets:
            violations.append(
                PolicyViolation(key=key, rule="P001", message=f"Required key '{key}' is missing")
            )

    forbidden_re = re.compile(forbidden_pattern) if forbidden_pattern else None
    key_re = re.compile(key_pattern) if key_pattern else None

    for key, value in secrets.items():
        if key_re and not key_re.match(key):
            violations.append(
                PolicyViolation(
                    key=key,
                    rule="P002",
                    message=f"Key '{key}' does not match required pattern '{key_pattern}'",
                )
            )

        if min_length and len(value) < min_length:
            violations.append(
                PolicyViolation(
                    key=key,
                    rule="P003",
                    message=f"Value for '{key}' is shorter than minimum length {min_length}",
                )
            )

        if forbidden_re and forbidden_re.search(value):
            violations.append(
                PolicyViolation(
                    key=key,
                    rule="P004",
                    message=f"Value for '{key}' matches forbidden pattern '{forbidden_pattern}'",
                )
            )

    return PolicyResult(violations=violations)
