"""Tests for Message Encryption for Web Push (RFC 8291)."""

import os

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from auto_authn.v2 import runtime_cfg
from auto_authn.v2.rfc8291 import decrypt_webpush, encrypt_webpush


@pytest.mark.unit
def test_encrypt_decrypt(monkeypatch):
    """Ciphertext decrypts back to the original message when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8291", True)
    key = AESGCM.generate_key(bit_length=128)
    nonce = os.urandom(12)
    message = b"hello"
    ct = encrypt_webpush(message, key, nonce)
    assert ct != message
    pt = decrypt_webpush(ct, key, nonce)
    assert pt == message


@pytest.mark.unit
def test_disabled_returns_plain(monkeypatch):
    """When disabled messages are returned unmodified."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8291", False)
    key = AESGCM.generate_key(bit_length=128)
    nonce = os.urandom(12)
    message = b"hi"
    assert encrypt_webpush(message, key, nonce) == message
