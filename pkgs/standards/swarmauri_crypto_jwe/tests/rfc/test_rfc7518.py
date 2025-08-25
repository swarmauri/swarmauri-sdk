import asyncio

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


@pytest.mark.unit
@pytest.mark.test
def test_rfc7518_ecdh_es() -> None:
    crypto = JweCrypto()
    sk = ec.generate_private_key(ec.SECP256R1())
    pk_pem = sk.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwe = asyncio.run(
        crypto.encrypt_compact(
            payload=b"rfc", alg=JWAAlg.ECDH_ES, enc=JWAAlg.A256GCM, key={"pub": pk_pem}
        )
    )
    res = asyncio.run(crypto.decrypt_compact(jwe, ecdh_private_key=sk))
    assert res.plaintext == b"rfc"
