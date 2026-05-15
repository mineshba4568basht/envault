"""CLI commands for managing key aliases."""

from __future__ import annotations

import click

from envault.alias import (
    list_aliases,
    remove_alias,
    resolve,
    reverse_lookup,
    set_alias,
)


@click.group("alias")
def alias_cmd() -> None:
    """Manage key aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def set_cmd(alias: str, key: str, vault_dir: str) -> None:
    """Create or update ALIAS pointing to KEY."""
    set_alias(vault_dir, alias, key)
    click.echo(f"Alias '{alias}' -> '{key}' saved.")


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--vault-dir", default=".envault", show_default=True)
def remove_cmd(alias: str, vault_dir: str) -> None:
    """Remove ALIAS."""
    remove_alias(vault_dir, alias)
    click.echo(f"Alias '{alias}' removed.")


@alias_cmd.command("resolve")
@click.argument("alias")
@click.option("--vault-dir", default=".envault", show_default=True)
def resolve_cmd(alias: str, vault_dir: str) -> None:
    """Print the real key that ALIAS maps to."""
    click.echo(resolve(vault_dir, alias))


@alias_cmd.command("list")
@click.option("--vault-dir", default=".envault", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all defined aliases."""
    aliases = list_aliases(vault_dir)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"{alias} -> {key}")


@alias_cmd.command("reverse")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def reverse_cmd(key: str, vault_dir: str) -> None:
    """List all aliases that point to KEY."""
    hits = reverse_lookup(vault_dir, key)
    if not hits:
        click.echo(f"No aliases point to '{key}'.")
        return
    for alias in sorted(hits):
        click.echo(alias)
