from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_open_for_many() -> None:
    crypto = EcdhEsA128KwMreCrypto()
    sk1 = ec.generate_private_key(ec.SECP256R1())
    pk1 = sk1.public_key()
    sk2 = ec.generate_private_key(ec.SECP256R1())

    env = await crypto.encrypt_for_many(
        [{"kid": "1", "version": 1, "kind": "cryptography_obj", "obj": pk1}],
        b"data",
    )

    pt = await crypto.open_for_many(
        [
            {"kind": "cryptography_obj", "obj": sk2},
            {"kind": "cryptography_obj", "obj": sk1},
        ],
        env,
    )
    assert pt == b"data"
