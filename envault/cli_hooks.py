"""CLI commands for inspecting registered lifecycle hooks."""
import click
from envault.hooks import registered_events, _VALID_EVENTS


@click.group("hooks")
def hooks_cmd():
    """Manage and inspect vault lifecycle hooks."""


@hooks_cmd.command("list")
def list_hooks():
    """List all lifecycle events and their registered hook counts."""
    counts = registered_events()
    any_registered = any(v > 0 for v in counts.values())
    if not any_registered:
        click.echo("No hooks registered.")
        return
    click.echo("Registered hooks:")
    for event in sorted(counts):
        count = counts[event]
        if count > 0:
            click.echo(f"  {event}: {count} hook(s)")


@hooks_cmd.command("events")
def list_events():
    """List all valid lifecycle event names."""
    click.echo("Valid lifecycle events:")
    for event in sorted(_VALID_EVENTS):
        click.echo(f"  {event}")
