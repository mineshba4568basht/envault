"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_PASSWORD=hunter2\nAPI_KEY=abc123"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, bytes)


def test_encrypt_output_differs_each_call():
    """Each encryption should produce a unique ciphertext (random salt)."""
    c1 = encrypt(PLAINTEXT, PASSWORD)
    c2 = encrypt(PLAINTEXT, PASSWORD)
    assert c1 != c2


def test_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(ciphertext, PASSWORD)
    assert recovered == PLAINTEXT


def test_decrypt_wrong_password_raises():
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-password")


def test_decrypt_corrupted_data_raises():
    ciphertext = bytearray(encrypt(PLAINTEXT, PASSWORD))
    ciphertext[20] ^= 0xFF  # flip a byte
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(bytes(ciphertext), PASSWORD)


def test_encrypt_empty_string():
    ciphertext = encrypt("", PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == ""


def test_encrypt_unicode_content():
    text = "SECRET=caf\u00e9\u2603"
    ciphertext = encrypt(text, PASSWORD)
    assert decrypt(ciphertext, PASSWORD) == text
