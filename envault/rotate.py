"""Key rotation support for envault vaults."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from envault.crypto import decrypt, encrypt
from envault.storage import VaultStorage
from envault.audit import record


def rotate_key(
    vault_dir: str | Path,
    old_password: str,
    new_password: str,
    vault_name: str = "default",
) -> int:
    """Re-encrypt all secrets in a vault under a new password.

    Reads every secret using *old_password*, then writes them back
    encrypted with *new_password*.  Returns the number of secrets
    that were rotated.

    Raises ``ValueError`` if the old password is incorrect (propagated
    from :func:`envault.crypto.decrypt`).
    """
    storage = VaultStorage(vault_dir, vault_name)
    raw = storage.load()  # raw dict: key -> ciphertext bytes (base64-stored)

    if not raw:
        return 0

    # Decrypt all values first so we fail fast on a wrong old password
    # before writing anything.
    plaintext: dict[str, str] = {}
    for key, ciphertext in raw.items():
        plaintext[key] = decrypt(ciphertext, old_password)

    # Re-encrypt with the new password and persist.
    rotated: dict[str, bytes] = {}
    for key, value in plaintext.items():
        rotated[key] = encrypt(value, new_password)

    storage.save(rotated)

    record(
        vault_dir,
        "rotate_key",
        {"vault": vault_name, "secrets_rotated": len(rotated)},
    )

    return len(rotated)


def rotate_key_for_all_vaults(
    vault_dir: str | Path,
    old_password: str,
    new_password: str,
) -> dict[str, int]:
    """Rotate the encryption key for every vault found in *vault_dir*.

    Returns a mapping of ``vault_name -> secrets_rotated``.
    """
    vault_dir = Path(vault_dir)
    results: dict[str, int] = {}

    for vault_file in sorted(vault_dir.glob("*.vault")):
        vault_name = vault_file.stem
        count = rotate_key(vault_dir, old_password, new_password, vault_name)
        results[vault_name] = count

    return results
