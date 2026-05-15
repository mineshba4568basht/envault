"""Tests for envault CLI hooks commands."""
import pytest
from click.testing import CliRunner
from envault.cli_hooks import hooks_cmd
from envault import hooks
from envault.hooks import EVENT_PRE_SET, EVENT_POST_SET


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_hooks():
    yield
    hooks.clear()


def test_list_hooks_no_hooks_registered(runner):
    result = runner.invoke(hooks_cmd, ["list"])
    assert result.exit_code == 0
    assert "No hooks registered" in result.output


def test_list_hooks_shows_registered(runner):
    hooks.register(EVENT_PRE_SET, lambda **kw: None)
    hooks.register(EVENT_PRE_SET, lambda **kw: None)
    hooks.register(EVENT_POST_SET, lambda **kw: None)
    result = runner.invoke(hooks_cmd, ["list"])
    assert result.exit_code == 0
    assert "pre_set: 2 hook(s)" in result.output
    assert "post_set: 1 hook(s)" in result.output


def test_list_events_shows_all_valid_events(runner):
    result = runner.invoke(hooks_cmd, ["events"])
    assert result.exit_code == 0
    for event in hooks._VALID_EVENTS:
        assert event in result.output


def test_list_hooks_only_shows_nonzero(runner):
    hooks.register(EVENT_PRE_SET, lambda **kw: None)
    result = runner.invoke(hooks_cmd, ["list"])
    assert "pre_set" in result.output
    # Events with 0 hooks should not appear
    assert "post_delete: 0" not in result.output
