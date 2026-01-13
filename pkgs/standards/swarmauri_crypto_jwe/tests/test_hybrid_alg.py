import asyncio
import base64
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from pqcrypto.kem import kyber768

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@pytest.mark.unit
@pytest.mark.test
def test_ecdh_es_x25519_mlkem768_round_trip() -> None:
    crypto = JweCrypto()

    recipient_x_priv = x25519.X25519PrivateKey.generate()
    recipient_x_pub = recipient_x_priv.public_key()
    recipient_x_pub_bytes = recipient_x_pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    mlkem_pub, mlkem_priv = kyber768.generate_keypair()

    jwe = asyncio.run(
        crypto.encrypt_compact(
            payload=b"hybrid",
            alg=JWAAlg.ECDH_ES_X25519_MLKEM768,
            enc=JWAAlg.A256GCM,
            key={
                "x25519": {
                    "kty": "OKP",
                    "crv": "X25519",
                    "x": _b64u(recipient_x_pub_bytes),
                },
                "mlkem768": base64.b64encode(mlkem_pub).decode("ascii"),
            },
        )
    )

    protected_b64 = jwe.split(".")[0]
    padding = "=" * ((4 - len(protected_b64) % 4) % 4)
    protected = json.loads(base64.urlsafe_b64decode(protected_b64 + padding))

    assert protected["alg"] == JWAAlg.ECDH_ES_X25519_MLKEM768.value
    assert protected["enc"] == JWAAlg.A256GCM.value
    assert protected["epk"]["crv"] == "X25519"
    assert protected["pqc"]["kem"] == "ML-KEM-768"
    assert isinstance(protected["pqc"]["ct"], str)

    result = asyncio.run(
        crypto.decrypt_compact(
            jwe,
            ecdh_private_key=recipient_x_priv,
            mlkem_private_key=mlkem_priv,
        )
    )

    assert result.plaintext == b"hybrid"
