"""CLI commands for syncing .env files with the vault."""
from __future__ import annotations

from pathlib import Path

import click

from envault.cli import cli, get_vault
from envault.sync import import_dotenv, sync_to_dotenv


@cli.command("import")
@click.argument("dotenv_file", default=".env", type=click.Path(exists=True, dir_okay=False))
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--no-overwrite",
    is_flag=True,
    default=False,
    help="Skip keys that already exist in the vault.",
)
def import_cmd(dotenv_file: str, vault_dir: str, password: str, no_overwrite: bool) -> None:
    """Import variables from a .env file into the vault."""
    vault = get_vault(vault_dir, password)
    imported, skipped = import_dotenv(vault, dotenv_file, overwrite=not no_overwrite)
    click.echo(f"Imported {imported} secret(s), skipped {skipped}.", err=False)


@cli.command("sync")
@click.argument("dotenv_file", default=".env", type=click.Path(dir_okay=False))
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--no-overwrite",
    is_flag=True,
    default=False,
    help="Skip keys already present in the target .env file.",
)
def sync_cmd(dotenv_file: str, vault_dir: str, password: str, no_overwrite: bool) -> None:
    """Write all vault secrets into a .env file."""
    vault = get_vault(vault_dir, password)
    written, skipped = sync_to_dotenv(vault, dotenv_file, overwrite=not no_overwrite)
    click.echo(f"Wrote {written} secret(s), skipped {skipped}.", err=False)
