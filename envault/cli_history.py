"""CLI commands for secret history inspection and rollback."""

import click
from datetime import datetime

from envault.cli import get_vault
from envault.history import get_history, get_version, clear_history
from envault.crypto import decrypt


@click.command("history")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def history_cmd(key: str, vault_dir: str, password: str) -> None:
    """Show the change history for KEY."""
    entries = get_history(vault_dir, key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    for i, entry in enumerate(entries):
        ts = datetime.fromtimestamp(entry["ts"]).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"  [{i}] {ts}  action={entry['action']}")


@click.command("rollback")
@click.argument("key")
@click.argument("version", type=int)
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def rollback_cmd(key: str, version: int, vault_dir: str, password: str) -> None:
    """Restore KEY to a previous VERSION (0-indexed)."""
    try:
        encrypted = get_version(vault_dir, key, version)
    except IndexError as exc:
        raise click.ClickException(str(exc))

    try:
        value = decrypt(encrypted, password)
    except Exception:
        raise click.ClickException("Decryption failed — wrong password or corrupted data.")

    vault = get_vault(vault_dir, password)
    vault.set(key, value)
    click.echo(f"Rolled back '{key}' to version {version}.")


@click.command("clear-history")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.confirmation_option(prompt="Are you sure you want to clear the history for this key?")
def clear_history_cmd(key: str, vault_dir: str, password: str) -> None:
    """Delete all history entries for KEY."""
    entries = get_history(vault_dir, key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    clear_history(vault_dir, key)
    click.echo(f"Cleared {len(entries)} history entry/entries for '{key}'.")
