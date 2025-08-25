"""Tests for Web Push message encryption (RFC 8291).

The helpers provide simple AES-128-GCM based encryption inspired by RFC 8291.
The tests confirm round-trip encryption and respect for the feature toggle.
"""

import os

import pytest

from auto_authn.v2.rfc8291 import decrypt_push_message, encrypt_push_message


@pytest.mark.unit
def test_encrypt_decrypt_round_trip():
    """Encryption and decryption work when the feature is enabled."""
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"hello"
    ciphertext = encrypt_push_message(plaintext, key, nonce, enabled=True)
    assert ciphertext != plaintext
    assert decrypt_push_message(ciphertext, key, nonce, enabled=True) == plaintext


@pytest.mark.unit
def test_disabled_returns_plain():
    """When disabled, messages are left unencrypted."""
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"data"
    ciphertext = encrypt_push_message(plaintext, key, nonce, enabled=False)
    assert ciphertext == plaintext
    assert decrypt_push_message(ciphertext, key, nonce, enabled=False) == ciphertext
