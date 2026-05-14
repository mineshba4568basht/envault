"""CLI commands for policy enforcement."""

import click

from envault.cli import get_vault
from envault.policy import check_policy


@click.command("policy-check")
@click.option("--vault-dir", default=".envault", show_default=True, help="Vault directory")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--require", "required_keys", multiple=True, metavar="KEY",
              help="Key that must exist (repeatable)")
@click.option("--forbidden-pattern", default=None, metavar="REGEX",
              help="Regex pattern that values must NOT match")
@click.option("--min-length", default=0, show_default=True,
              help="Minimum value length for all secrets")
@click.option("--key-pattern", default=None, metavar="REGEX",
              help="Regex that every key must match")
def policy_check_cmd(
    vault_dir: str,
    password: str,
    required_keys: tuple,
    forbidden_pattern: str | None,
    min_length: int,
    key_pattern: str | None,
) -> None:
    """Check vault secrets against a policy and report violations."""
    vault = get_vault(vault_dir, password)
    secrets = {k: vault.get(k) for k in vault.list()}

    result = check_policy(
        secrets,
        required_keys=list(required_keys) if required_keys else None,
        forbidden_pattern=forbidden_pattern,
        min_length=min_length,
        key_pattern=key_pattern,
    )

    if result.ok:
        click.secho("✔ Policy check passed — no violations found.", fg="green")
        return

    click.secho(f"✖ Policy check failed — {len(result.violations)} violation(s):", fg="red")
    for v in result.violations:
        click.echo(f"  [{v.rule}] {v.message}")
    raise SystemExit(1)
