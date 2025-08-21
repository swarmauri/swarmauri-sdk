import asyncio

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.i9n
@pytest.mark.test
def test_rsa_encrypt_decrypt_functional() -> None:
    crypto = JweCrypto()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_pem = sk.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    sk_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    jwe = asyncio.run(
        crypto.encrypt_compact(
            payload=b"functional",
            alg="RSA-OAEP-256",
            enc="A256GCM",
            key={"pub": pk_pem},
        )
    )
    res = asyncio.run(crypto.decrypt_compact(jwe, rsa_private_pem=sk_pem))
    assert res.plaintext == b"functional"
