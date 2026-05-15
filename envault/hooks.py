"""Lifecycle hooks for envault vault operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Hook event names
EVENT_PRE_SET = "pre_set"
EVENT_POST_SET = "post_set"
EVENT_PRE_GET = "pre_get"
EVENT_POST_GET = "post_get"
EVENT_PRE_DELETE = "pre_delete"
EVENT_POST_DELETE = "post_delete"

_VALID_EVENTS = {
    EVENT_PRE_SET, EVENT_POST_SET,
    EVENT_PRE_GET, EVENT_POST_GET,
    EVENT_PRE_DELETE, EVENT_POST_DELETE,
}

# Registry: event -> list of callables
_registry: Dict[str, List[Callable]] = {event: [] for event in _VALID_EVENTS}


def _hooks_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".hooks.json"


def register(event: str, fn: Callable) -> None:
    """Register a callback for a lifecycle event."""
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(_VALID_EVENTS)}")
    _registry[event].append(fn)


def unregister(event: str, fn: Callable) -> None:
    """Remove a previously registered callback."""
    if event in _registry and fn in _registry[event]:
        _registry[event].remove(fn)


def fire(event: str, **kwargs) -> None:
    """Fire all callbacks registered for an event, passing kwargs as context."""
    for fn in _registry.get(event, []):
        fn(event=event, **kwargs)


def clear(event: Optional[str] = None) -> None:
    """Clear all hooks for a specific event, or all events if None."""
    if event is not None:
        _registry[event] = []
    else:
        for key in _registry:
            _registry[key] = []


def registered_events() -> Dict[str, int]:
    """Return a mapping of event -> number of registered hooks."""
    return {event: len(fns) for event, fns in _registry.items()}
