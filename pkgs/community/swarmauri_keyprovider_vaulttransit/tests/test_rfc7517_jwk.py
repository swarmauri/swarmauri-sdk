from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_keyprovider_vaulttransit.VaultTransitKeyProvider import _pem_to_jwk


def test_pem_to_jwk_rsa():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwk = _pem_to_jwk(pem)
    assert jwk["kty"] == "RSA"
    assert "n" in jwk and "e" in jwk
