"""CLI commands for managing per-key access control."""

import click
from envault.cli import get_vault
from envault import access


@click.group("access")
def access_cmd():
    """Manage read/write permissions for vault keys."""


@access_cmd.command("grant")
@click.argument("key")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.pass_context
def grant_cmd(ctx: click.Context, key: str, permission: str) -> None:
    """Grant a permission to a key."""
    vault = get_vault(ctx)
    access.grant(vault.storage.vault_dir, key, permission)
    click.echo(f"Granted '{permission}' on '{key}'.")


@access_cmd.command("revoke")
@click.argument("key")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.pass_context
def revoke_cmd(ctx: click.Context, key: str, permission: str) -> None:
    """Revoke a permission from a key."""
    vault = get_vault(ctx)
    access.revoke(vault.storage.vault_dir, key, permission)
    click.echo(f"Revoked '{permission}' on '{key}'.")


@access_cmd.command("show")
@click.argument("key")
@click.pass_context
def show_cmd(ctx: click.Context, key: str) -> None:
    """Show permissions for a key."""
    vault = get_vault(ctx)
    perms = access.get_permissions(vault.storage.vault_dir, key)
    click.echo(f"{key}: {', '.join(perms)}")


@access_cmd.command("list")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """List all keys with explicit access rules."""
    vault = get_vault(ctx)
    restricted = access.list_restricted_keys(vault.storage.vault_dir)
    if not restricted:
        click.echo("No explicit access rules defined.")
        return
    for key, perms in sorted(restricted.items()):
        click.echo(f"  {key}: {', '.join(perms)}")
