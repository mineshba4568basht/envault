"""Command-line interface for envault."""

import sys
import click
from envault.vault import Vault


def get_vault(path: str, password: str) -> Vault:
    return Vault(storage_path=path, password=password)


@click.group()
def cli():
    """envault — secure .env secrets manager."""
    pass


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault directory.")
@click.password_option("--password", prompt="Vault password", help="Master password for the vault.")
def set_secret(key, value, vault_path, password):
    """Set a secret KEY to VALUE in the vault."""
    v = get_vault(vault_path, password)
    v.set(key, value)
    click.echo(f"✔ Secret '{key}' stored successfully.")


@cli.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault directory.")
@click.option("--password", prompt="Vault password", hide_input=True, help="Master password for the vault.")
def get_secret(key, vault_path, password):
    """Get a secret by KEY from the vault."""
    v = get_vault(vault_path, password)
    try:
        value = v.get(key)
        click.echo(value)
    except KeyError:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault directory.")
@click.option("--password", prompt="Vault password", hide_input=True, help="Master password for the vault.")
def delete_secret(key, vault_path, password):
    """Delete a secret by KEY from the vault."""
    v = get_vault(vault_path, password)
    try:
        v.delete(key)
        click.echo(f"✔ Secret '{key}' deleted.")
    except KeyError:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault directory.")
@click.option("--password", prompt="Vault password", hide_input=True, help="Master password for the vault.")
def list_secrets(vault_path, password):
    """List all secret keys stored in the vault."""
    v = get_vault(vault_path, password)
    keys = v.list_keys()
    if not keys:
        click.echo("No secrets stored.")
    else:
        for key in sorted(keys):
            click.echo(key)


if __name__ == "__main__":
    cli()
