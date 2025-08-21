from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

from swarmauri_core.keys.types import KeyAlg
from swarmauri_keyprovider_vaulttransit.VaultTransitKeyProvider import (
    VaultTransitKeyProvider,
    _pem_to_jwk,
)


class DummyProvider(VaultTransitKeyProvider):
    def __init__(self) -> None:  # pragma: no cover - used only in tests
        self._prefer_vault_rng = False
        self._client = SimpleNamespace(
            sys=SimpleNamespace(generate_random_bytes=lambda n_bytes: {})
        )


@pytest.mark.unit
@pytest.mark.parametrize(
    "alg,expected",
    [
        (KeyAlg.AES256_GCM, ("aes256-gcm96", "encryption")),
        (KeyAlg.RSA_OAEP_SHA256, ("rsa-3072", "encryption")),
        (KeyAlg.RSA_PSS_SHA256, ("rsa-3072", "signing")),
        (KeyAlg.ECDSA_P256_SHA256, ("ecdsa-p256", "signing")),
        (KeyAlg.ED25519, ("ed25519", "signing")),
    ],
)
def test_vault_type_for_alg(alg, expected):
    assert VaultTransitKeyProvider._vault_type_for_alg(alg) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "purpose,expected",
    [("encryption", "encryption-key"), ("signing", "signing-key")],
)
def test_export_type_for_purpose(purpose, expected):
    dummy = DummyProvider()
    assert dummy._export_type_for_purpose(purpose) == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_random_bytes_and_hkdf():
    dummy = DummyProvider()
    rnd = await dummy.random_bytes(8)
    assert len(rnd) == 8
    out = await dummy.hkdf(b"ikm", salt=b"s", info=b"i", length=16)
    assert len(out) == 16


@pytest.mark.unit
def test_pem_to_jwk_rsa():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    jwk = _pem_to_jwk(pem)
    assert jwk["kty"] == "RSA" and "n" in jwk and "e" in jwk


@pytest.mark.unit
def test_pem_to_jwk_ec():
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    jwk = _pem_to_jwk(pem)
    assert jwk["kty"] == "EC" and jwk["crv"] == "P-256"


@pytest.mark.unit
def test_pem_to_jwk_ed25519():
    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    jwk = _pem_to_jwk(pem)
    assert jwk["kty"] == "OKP" and jwk["crv"] == "Ed25519"
