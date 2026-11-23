from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import pytest

from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_crypto_ecdh_es_a128kw import ECDHESA128KWCrypto


@pytest.mark.asyncio
async def test_wrap_then_unwrap_roundtrip():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()

    priv_pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    pub_pem = pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    wrap_key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pub_pem,
    )
    unwrap_key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.EC,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=priv_pem,
    )

    crypto = ECDHESA128KWCrypto()
    dek = b"0" * 16
    wrapped = await crypto.wrap(wrap_key, dek=dek)
    unwrapped = await crypto.unwrap(unwrap_key, wrapped)
    assert unwrapped == dek
