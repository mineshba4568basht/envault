"""Encryption and decryption utilities for envault secrets."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(plaintext: str, password: str) -> bytes:
    """Encrypt plaintext string using a password.

    Returns salt + encrypted token as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    return salt + token


def decrypt(ciphertext: bytes, password: str) -> str:
    """Decrypt ciphertext bytes using a password.

    Raises ValueError on bad password or corrupted data.
    """
    salt = ciphertext[:SALT_SIZE]
    token = ciphertext[SALT_SIZE:]
    key = derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid password or corrupted data.") from exc
