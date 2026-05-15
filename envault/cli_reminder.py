"""CLI commands for secret rotation reminders."""

import click

from envault.cli import get_vault
from envault import reminder as rem


@click.group("reminder")
def reminder_cmd() -> None:
    """Manage secret rotation reminders."""


@reminder_cmd.command("mark")
@click.argument("key")
@click.option("--vault-dir", default=".vault", show_default=True)
def mark_cmd(key: str, vault_dir: str) -> None:
    """Mark KEY as rotated right now."""
    rem.mark_rotated(vault_dir, key)
    click.echo(f"Marked '{key}' as rotated.")


@reminder_cmd.command("status")
@click.argument("key")
@click.option("--vault-dir", default=".vault", show_default=True)
def status_cmd(key: str, vault_dir: str) -> None:
    """Show how long ago KEY was last rotated."""
    age = rem.days_since_rotation(vault_dir, key)
    if age is None:
        click.echo(f"'{key}' has never been marked as rotated.")
    else:
        click.echo(f"'{key}' was last rotated {age:.1f} day(s) ago.")


@reminder_cmd.command("stale")
@click.option("--vault-dir", default=".vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--max-age", default=90.0, show_default=True, help="Max age in days before a key is considered stale.")
def stale_cmd(vault_dir: str, password: str, max_age: float) -> None:
    """List keys that are overdue for rotation."""
    vault = get_vault(vault_dir, password)
    keys = vault.list()
    overdue = rem.stale_keys(vault_dir, keys, max_age_days=max_age)
    if not overdue:
        click.echo("All keys are up to date.")
    else:
        click.echo(f"{len(overdue)} stale key(s):")
        for k in overdue:
            age = rem.days_since_rotation(vault_dir, k)
            age_str = f"{age:.1f}d" if age is not None else "never rotated"
            click.echo(f"  {k}  ({age_str})")
