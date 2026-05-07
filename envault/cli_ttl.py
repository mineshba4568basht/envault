"""CLI commands for managing secret TTLs."""

import click
from envault.cli import get_vault
from envault import ttl as ttl_mod


@click.command("ttl-set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ttl_set_cmd(key: str, seconds: int, vault_dir: str, password: str) -> None:
    """Set a TTL (in seconds) for KEY."""
    vault = get_vault(vault_dir, password)
    try:
        vault.get(key)
    except Exception:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    ttl_mod.set_ttl(vault_dir, key, seconds)
    click.echo(f"TTL of {seconds}s set for '{key}'.")


@click.command("ttl-get")
@click.argument("key")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ttl_get_cmd(key: str, vault_dir: str, password: str) -> None:
    """Show remaining TTL for KEY."""
    get_vault(vault_dir, password)  # validate password
    remaining = ttl_mod.get_ttl(vault_dir, key)
    if remaining is None:
        click.echo(f"'{key}' has no TTL (permanent).")
    elif ttl_mod.is_expired(vault_dir, key):
        click.echo(f"'{key}' has EXPIRED.")
    else:
        click.echo(f"'{key}' expires in {remaining:.1f}s.")


@click.command("ttl-purge")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def ttl_purge_cmd(vault_dir: str, password: str) -> None:
    """Remove all expired TTL entries from the vault metadata."""
    get_vault(vault_dir, password)  # validate password
    expired = ttl_mod.purge_expired(vault_dir)
    if expired:
        for k in expired:
            click.echo(f"Purged expired TTL for '{k}'.")
    else:
        click.echo("No expired TTL entries found.")
