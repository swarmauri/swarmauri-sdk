"""Tests for Web Push message encryption (RFC 8291).

The helpers provide simple AES-128-GCM based encryption inspired by RFC 8291.
The tests confirm round-trip encryption and respect for the feature toggle.
"""

import os

import pytest

from tigrbl_auth.rfc.rfc8291 import (
    RFC8291_SPEC_URL,
    decrypt_push_message,
    encrypt_push_message,
)
from tigrbl_auth.runtime_cfg import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_encrypt_decrypt_round_trip():
    """Encryption and decryption work when the feature is enabled."""
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"hello"
    ciphertext = await encrypt_push_message(plaintext, key, nonce, enabled=True)
    assert ciphertext != plaintext
    assert await decrypt_push_message(ciphertext, key, nonce, enabled=True) == plaintext


@pytest.mark.unit
@pytest.mark.asyncio
async def test_disabled_returns_plain():
    """When disabled, messages are left unencrypted."""
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"data"
    ciphertext = await encrypt_push_message(plaintext, key, nonce, enabled=False)
    assert ciphertext == plaintext
    assert (
        await decrypt_push_message(ciphertext, key, nonce, enabled=False) == ciphertext
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_respects_runtime_setting(monkeypatch):
    """Default behaviour follows the runtime configuration toggle."""
    key = os.urandom(16)
    nonce = os.urandom(12)
    plaintext = b"hello"
    monkeypatch.setattr(settings, "enable_rfc8291", False)
    assert await encrypt_push_message(plaintext, key, nonce) == plaintext
    monkeypatch.setattr(settings, "enable_rfc8291", True)
    ciphertext = await encrypt_push_message(plaintext, key, nonce)
    assert await decrypt_push_message(ciphertext, key, nonce) == plaintext


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_key_or_nonce_length():
    """Incorrect key or nonce lengths raise errors when enabled."""
    key = os.urandom(15)
    nonce = os.urandom(12)
    with pytest.raises(ValueError):
        await encrypt_push_message(b"data", key, nonce, enabled=True)
    key = os.urandom(16)
    nonce = os.urandom(11)
    with pytest.raises(ValueError):
        await decrypt_push_message(b"data", key, nonce, enabled=True)


@pytest.mark.unit
def test_spec_url_constant():
    """Spec URL constant references the official RFC document."""
    assert RFC8291_SPEC_URL.endswith("rfc8291")
