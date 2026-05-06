"""CLI commands for exporting and importing encrypted vault bundles."""

import click
from envault.cli import get_vault
from envault.share import export_bundle, import_bundle_from_file


@click.command("export-bundle")
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--output", "-o", default=None, help="Write bundle to this file path.")
def export_bundle_cmd(vault_dir: str, password: str, output: str) -> None:
    """Export all secrets as an encrypted portable bundle."""
    vault = get_vault(vault_dir, password)
    bundle = export_bundle(vault, password, output_path=output)
    if output:
        click.echo(f"Bundle written to {output}")
    else:
        click.echo(bundle)


@click.command("import-bundle")
@click.argument("bundle_file")
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys.",
)
def import_bundle_cmd(bundle_file: str, vault_dir: str, password: str, overwrite: bool) -> None:
    """Import secrets from an encrypted bundle file into the vault."""
    vault = get_vault(vault_dir, password)
    try:
        count = import_bundle_from_file(bundle_file, password, vault, overwrite=overwrite)
        click.echo(f"Imported {count} secret(s).")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
