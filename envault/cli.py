"""Main CLI entry point for envault."""

import click
from envault.vault import Vault, KeyNotFoundError
from envault.storage import VaultStorage
from envault.cli_sync import import_cmd, sync_cmd
from envault.cli_share import export_bundle_cmd, import_bundle_cmd
from envault.cli_history import history_cmd, rollback_cmd, clear_history_cmd
from envault.cli_ttl import ttl_set_cmd, ttl_get_cmd, ttl_purge_cmd
from envault.cli_policy import policy_check_cmd
from envault.cli_access import access_cmd


def get_vault(ctx: click.Context) -> Vault:
    vault_dir = ctx.obj["vault_dir"]
    password = ctx.obj["password"]
    storage = VaultStorage(vault_dir)
    return Vault(storage, password)


@click.group()
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True, help="Master password.")
@click.pass_context
def cli(ctx: click.Context, vault_dir: str, password: str) -> None:
    """envault — secure .env secrets manager."""
    ctx.ensure_object(dict)
    ctx.obj["vault_dir"] = vault_dir
    ctx.obj["password"] = password


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_secret(ctx: click.Context, key: str, value: str) -> None:
    """Store a secret."""
    vault = get_vault(ctx)
    vault.set(key, value)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.argument("key")
@click.pass_context
def get_secret(ctx: click.Context, key: str) -> None:
    """Retrieve a secret."""
    vault = get_vault(ctx)
    try:
        click.echo(vault.get(key))
    except KeyNotFoundError:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command("delete")
@click.argument("key")
@click.pass_context
def delete_secret(ctx: click.Context, key: str) -> None:
    """Delete a secret."""
    vault = get_vault(ctx)
    try:
        vault.delete(key)
        click.echo(f"Deleted '{key}'.")
    except KeyNotFoundError:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command("list")
@click.pass_context
def list_secrets(ctx: click.Context) -> None:
    """List all secret keys."""
    vault = get_vault(ctx)
    keys = vault.keys()
    if not keys:
        click.echo("No secrets stored.")
    for key in sorted(keys):
        click.echo(key)


cli.add_command(import_cmd, "import")
cli.add_command(sync_cmd, "sync")
cli.add_command(export_bundle_cmd, "export-bundle")
cli.add_command(import_bundle_cmd, "import-bundle")
cli.add_command(history_cmd, "history")
cli.add_command(rollback_cmd, "rollback")
cli.add_command(clear_history_cmd, "clear-history")
cli.add_command(ttl_set_cmd, "ttl-set")
cli.add_command(ttl_get_cmd, "ttl-get")
cli.add_command(ttl_purge_cmd, "ttl-purge")
cli.add_command(policy_check_cmd, "policy-check")
cli.add_command(access_cmd)
