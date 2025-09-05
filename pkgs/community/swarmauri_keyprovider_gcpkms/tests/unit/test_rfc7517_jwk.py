import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_keyprovider_gcpkms.GcpKmsKeyProvider import _jwk_from_pem_public_key


@pytest.mark.unit
def test_rfc7517_jwk_rsa():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    jwk = _jwk_from_pem_public_key(pem)
    assert jwk["kty"] == "RSA"
    assert "n" in jwk and "e" in jwk


@pytest.mark.unit
def test_rfc7517_jwk_ec():
    key = ec.generate_private_key(ec.SECP256R1())
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    jwk = _jwk_from_pem_public_key(pem)
    assert jwk["kty"] == "EC"
    assert jwk["crv"] == "P-256"
    assert "x" in jwk and "y" in jwk
