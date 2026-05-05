"""High-level Vault interface combining crypto and storage."""

from typing import Dict, Optional

from envault.crypto import decrypt, encrypt
from envault.storage import VaultStorage, VaultStorageError


class Vault:
    """Manages encrypted key/value secrets backed by a storage backend."""

    def __init__(self, password: str, storage: Optional[VaultStorage] = None):
        self.password = password
        self.storage = storage or VaultStorage()

    def set(self, key: str, value: str) -> None:
        """Encrypt and store a secret under the given key."""
        data = self.storage.load()
        data[key] = encrypt(value.encode(), self.password).hex()
        self.storage.save(data)

    def get(self, key: str) -> str:
        """Retrieve and decrypt a secret by key.

        Raises KeyError if key does not exist.
        Raises ValueError if decryption fails (wrong password or corruption).
        """
        data = self.storage.load()
        if key not in data:
            raise KeyError(f"Secret '{key}' not found in vault.")
        raw = bytes.fromhex(data[key])
        return decrypt(raw, self.password).decode()

    def delete(self, key: str) -> None:
        """Remove a secret from the vault.

        Raises KeyError if key does not exist.
        """
        data = self.storage.load()
        if key not in data:
            raise KeyError(f"Secret '{key}' not found in vault.")
        del data[key]
        self.storage.save(data)

    def list_keys(self) -> list:
        """Return a sorted list of all stored secret keys."""
        return sorted(self.storage.load().keys())

    def export_env(self) -> Dict[str, str]:
        """Decrypt and return all secrets as a plain key/value dict."""
        data = self.storage.load()
        return {
            key: decrypt(bytes.fromhex(val), self.password).decode()
            for key, val in data.items()
        }
