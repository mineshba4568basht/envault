"""Template rendering: substitute vault secrets into template strings."""

import re
from typing import Optional

from envault.vault import Vault, KeyNotFoundError

# Matches {{ KEY_NAME }} or {{KEY_NAME}} with optional whitespace
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


class TemplateMissingKeyError(Exception):
    """Raised when a template references a key not present in the vault."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Template references missing vault key: {key!r}")


def render_string(
    template: str,
    vault: Vault,
    *,
    strict: bool = True,
    default: Optional[str] = None,
) -> str:
    """Render *template* by replacing ``{{ KEY }}`` placeholders with vault values.

    Parameters
    ----------
    template:
        A string containing zero or more ``{{ KEY }}`` placeholders.
    vault:
        The :class:`~envault.vault.Vault` instance to read secrets from.
    strict:
        If *True* (default), raise :class:`TemplateMissingKeyError` when a
        placeholder key is not found in the vault.  If *False*, replace missing
        keys with *default*.
    default:
        Fallback value used when *strict* is *False* and a key is missing.
    """

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        try:
            return vault.get(key)
        except KeyNotFoundError:
            if strict:
                raise TemplateMissingKeyError(key)
            return default if default is not None else match.group(0)

    return _PLACEHOLDER_RE.sub(_replace, template)


def render_file(
    src_path: str,
    dst_path: str,
    vault: Vault,
    *,
    strict: bool = True,
    default: Optional[str] = None,
) -> int:
    """Read *src_path*, render placeholders, and write the result to *dst_path*.

    Returns the number of substitutions made.
    """
    with open(src_path, "r", encoding="utf-8") as fh:
        source = fh.read()

    placeholders = _PLACEHOLDER_RE.findall(source)
    rendered = render_string(source, vault, strict=strict, default=default)

    with open(dst_path, "w", encoding="utf-8") as fh:
        fh.write(rendered)

    return len(placeholders)
