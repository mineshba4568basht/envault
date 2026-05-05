"""Storage backends for encrypted .env vault files."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_VAULT_DIR = Path.home() / ".envault"
DEFAULT_VAULT_FILE = "vault.json"


class VaultStorage:
    """Local filesystem storage backend for encrypted vault data."""

    def __init__(self, vault_dir: Optional[Path] = None):
        self.vault_dir = Path(vault_dir) if vault_dir else DEFAULT_VAULT_DIR
        self.vault_path = self.vault_dir / DEFAULT_VAULT_FILE

    def _ensure_dir(self) -> None:
        """Create vault directory with restricted permissions if it doesn't exist."""
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.vault_dir, 0o700)

    def load(self) -> Dict[str, str]:
        """Load all encrypted entries from vault. Returns empty dict if vault missing."""
        if not self.vault_path.exists():
            return {}
        try:
            with open(self.vault_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise VaultStorageError(f"Failed to read vault: {e}") from e

    def save(self, data: Dict[str, str]) -> None:
        """Persist encrypted entries to vault file with restricted permissions."""
        self._ensure_dir()
        try:
            with open(self.vault_path, "w") as f:
                json.dump(data, f, indent=2)
            os.chmod(self.vault_path, 0o600)
        except OSError as e:
            raise VaultStorageError(f"Failed to write vault: {e}") from e

    def delete(self) -> None:
        """Remove the vault file entirely."""
        if self.vault_path.exists():
            self.vault_path.unlink()

    def exists(self) -> bool:
        """Return True if a vault file exists on disk."""
        return self.vault_path.exists()


class VaultStorageError(Exception):
    """Raised when a storage operation fails."""
