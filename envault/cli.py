"""CLI entry point for envault."""

import sys
import click

from envault.vault import Vault
from envault.export import export_secrets, SUPPORTED_FORMATS


def get_vault(vault_dir: str, password: str) -> Vault:
    return Vault(vault_dir=vault_dir, password=password)


@click.group()
def cli():
    """envault — simple encrypted secrets manager."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set_secret(key, value, vault_dir, password):
    """Set a secret KEY to VALUE."""
    vault = get_vault(vault_dir, password)
    vault.set(key, value)
    click.echo(f"Secret '{key}' set.")


@cli.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def get_secret(key, vault_dir, password):
    """Get the value of secret KEY."""
    vault = get_vault(vault_dir, password)
    try:
        click.echo(vault.get(key))
    except KeyError:
        click.echo(f"Error: key '{key}' not found.", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def delete_secret(key, vault_dir, password):
    """Delete secret KEY."""
    vault = get_vault(vault_dir, password)
    try:
        vault.delete(key)
        click.echo(f"Secret '{key}' deleted.")
    except KeyError:
        click.echo(f"Error: key '{key}' not found.", err=True)
        sys.exit(1)


@cli.command("export")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format for exported secrets.",
)
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
def export_cmd(vault_dir, password, fmt, output):
    """Export all secrets in the specified format."""
    vault = get_vault(vault_dir, password)
    secrets = vault.all()
    result = export_secrets(secrets, fmt)
    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Exported {len(secrets)} secret(s) to '{output}'.")
    else:
        click.echo(result, nl=False)


if __name__ == "__main__":
    cli()
