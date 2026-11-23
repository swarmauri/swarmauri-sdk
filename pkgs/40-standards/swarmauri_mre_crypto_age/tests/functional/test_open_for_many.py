from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_open_for_many() -> None:
    crypto = AgeMreCrypto()
    sk1 = X25519PrivateKey.generate()
    pk1 = sk1.public_key()
    sk2 = X25519PrivateKey.generate()

    env = await crypto.encrypt_for_many(
        [{"kind": "cryptography_obj", "obj": pk1}], b"data"
    )

    pt = await crypto.open_for_many(
        [
            {"kind": "cryptography_obj", "obj": sk2},
            {"kind": "cryptography_obj", "obj": sk1},
        ],
        env,
    )
    assert pt == b"data"
