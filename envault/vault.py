"""Core Vault — thin wrapper around VaultStorage with optional history tracking."""

from __future__ import annotations

from typing import List

from envault.storage import VaultStorage
from envault.crypto import encrypt, decrypt


class KeyNotFoundError(KeyError):
    """Raised when a requested key is absent from the vault."""


class Vault:
    def __init__(self, vault_dir: str, password: str, track_history: bool = True) -> None:
        self._storage = VaultStorage(vault_dir)
        self._password = password
        self._vault_dir = vault_dir
        self._track_history = track_history

    # ------------------------------------------------------------------
    def set(self, key: str, value: str) -> None:
        encrypted = encrypt(value, self._password)
        if self._track_history:
            from envault.history import record_change
            record_change(self._vault_dir, key, encrypted, action="set")
        data = self._storage.load()
        data[key] = encrypted.hex()
        self._storage.save(data)

    def get(self, key: str) -> str:
        data = self._storage.load()
        if key not in data:
            raise KeyNotFoundError(key)
        return decrypt(bytes.fromhex(data[key]), self._password)

    def delete(self, key: str) -> None:
        data = self._storage.load()
        if key not in data:
            raise KeyNotFoundError(key)
        if self._track_history:
            from envault.history import record_change
            record_change(self._vault_dir, key, bytes.fromhex(data[key]), action="delete")
        del data[key]
        self._storage.save(data)

    def keys(self) -> List[str]:
        return list(self._storage.load().keys())

    def exists(self, key: str) -> bool:
        return key in self._storage.load()

    def all_secrets(self) -> dict:
        return {k: self.get(k) for k in self.keys()}
