"""Environment profile support — named sets of secrets for different environments (dev/staging/prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_PROFILE = "default"


def _profiles_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".profiles.json"


def _load_profiles(vault_dir: str) -> Dict[str, List[str]]:
    """Load the profiles index: maps profile name -> list of secret keys."""
    p = _profiles_path(vault_dir)
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)


def _save_profiles(vault_dir: str, data: Dict[str, List[str]]) -> None:
    p = _profiles_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def assign_key(vault_dir: str, profile: str, key: str) -> None:
    """Assign a secret key to a named profile."""
    profiles = _load_profiles(vault_dir)
    keys = profiles.setdefault(profile, [])
    if key not in keys:
        keys.append(key)
    _save_profiles(vault_dir, profiles)


def unassign_key(vault_dir: str, profile: str, key: str) -> bool:
    """Remove a key from a profile. Returns True if it was present."""
    profiles = _load_profiles(vault_dir)
    keys = profiles.get(profile, [])
    if key not in keys:
        return False
    keys.remove(key)
    if not keys:
        del profiles[profile]
    else:
        profiles[profile] = keys
    _save_profiles(vault_dir, profiles)
    return True


def list_profiles(vault_dir: str) -> List[str]:
    """Return all defined profile names."""
    return list(_load_profiles(vault_dir).keys())


def get_profile_keys(vault_dir: str, profile: str) -> List[str]:
    """Return the keys assigned to a profile (empty list if unknown)."""
    return _load_profiles(vault_dir).get(profile, [])


def get_key_profiles(vault_dir: str, key: str) -> List[str]:
    """Return all profiles that contain a given key."""
    profiles = _load_profiles(vault_dir)
    return [name for name, keys in profiles.items() if key in keys]


def delete_profile(vault_dir: str, profile: str) -> bool:
    """Delete an entire profile. Returns True if it existed."""
    profiles = _load_profiles(vault_dir)
    if profile not in profiles:
        return False
    del profiles[profile]
    _save_profiles(vault_dir, profiles)
    return True
