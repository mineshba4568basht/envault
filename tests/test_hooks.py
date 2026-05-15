"""Tests for envault.hooks lifecycle hook system."""
import pytest
from envault import hooks
from envault.hooks import (
    register, unregister, fire, clear, registered_events,
    EVENT_PRE_SET, EVENT_POST_SET, EVENT_PRE_DELETE,
)


@pytest.fixture(autouse=True)
def reset_hooks():
    """Ensure a clean hook registry for every test."""
    yield
    clear()


def test_register_and_fire_calls_callback():
    calls = []
    register(EVENT_PRE_SET, lambda **kw: calls.append(kw))
    fire(EVENT_PRE_SET, key="FOO", vault_dir="/tmp")
    assert len(calls) == 1
    assert calls[0]["key"] == "FOO"
    assert calls[0]["event"] == EVENT_PRE_SET


def test_multiple_hooks_all_called():
    results = []
    register(EVENT_POST_SET, lambda **kw: results.append("a"))
    register(EVENT_POST_SET, lambda **kw: results.append("b"))
    fire(EVENT_POST_SET, key="X")
    assert results == ["a", "b"]


def test_fire_unknown_event_does_not_raise():
    # firing an unregistered-but-valid event with no hooks is safe
    fire(EVENT_PRE_DELETE, key="GONE")


def test_register_invalid_event_raises():
    with pytest.raises(ValueError, match="Unknown event"):
        register("invalid_event", lambda **kw: None)


def test_unregister_removes_callback():
    calls = []
    fn = lambda **kw: calls.append(1)
    register(EVENT_PRE_SET, fn)
    unregister(EVENT_PRE_SET, fn)
    fire(EVENT_PRE_SET, key="K")
    assert calls == []


def test_unregister_nonexistent_is_safe():
    fn = lambda **kw: None
    unregister(EVENT_PRE_SET, fn)  # should not raise


def test_clear_specific_event():
    register(EVENT_PRE_SET, lambda **kw: None)
    register(EVENT_POST_SET, lambda **kw: None)
    clear(EVENT_PRE_SET)
    counts = registered_events()
    assert counts[EVENT_PRE_SET] == 0
    assert counts[EVENT_POST_SET] == 1


def test_clear_all_events():
    register(EVENT_PRE_SET, lambda **kw: None)
    register(EVENT_POST_SET, lambda **kw: None)
    clear()
    counts = registered_events()
    assert all(v == 0 for v in counts.values())


def test_registered_events_returns_correct_counts():
    register(EVENT_PRE_SET, lambda **kw: None)
    register(EVENT_PRE_SET, lambda **kw: None)
    counts = registered_events()
    assert counts[EVENT_PRE_SET] == 2


def test_hook_receives_all_kwargs():
    received = {}
    def capture(**kw):
        received.update(kw)
    register(EVENT_POST_SET, capture)
    fire(EVENT_POST_SET, key="DB_URL", vault_dir="/vaults/dev")
    assert received["key"] == "DB_URL"
    assert received["vault_dir"] == "/vaults/dev"
    assert received["event"] == EVENT_POST_SET
