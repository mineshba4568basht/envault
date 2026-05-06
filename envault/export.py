"""Export vault secrets to various formats (.env, JSON, shell)."""

import json
from typing import Dict


SUPPORTED_FORMATS = ("dotenv", "json", "shell")


def export_dotenv(secrets: Dict[str, str]) -> str:
    """Export secrets as a .env file string."""
    lines = []
    for key, value in sorted(secrets.items()):
        # Wrap value in quotes if it contains spaces or special chars
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(secrets: Dict[str, str]) -> str:
    """Export secrets as a JSON string."""
    return json.dumps(secrets, indent=2, sort_keys=True) + "\n"


def export_shell(secrets: Dict[str, str]) -> str:
    """Export secrets as shell export statements."""
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def export_secrets(secrets: Dict[str, str], fmt: str) -> str:
    """Export secrets in the specified format.

    Args:
        secrets: Dictionary of secret key-value pairs.
        fmt: Output format — one of 'dotenv', 'json', 'shell'.

    Returns:
        Formatted string representation of secrets.

    Raises:
        ValueError: If the format is not supported.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "dotenv":
        return export_dotenv(secrets)
    if fmt == "json":
        return export_json(secrets)
    return export_shell(secrets)
