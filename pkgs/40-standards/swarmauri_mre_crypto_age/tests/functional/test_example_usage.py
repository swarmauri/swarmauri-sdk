from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto


@pytest.mark.example
@pytest.mark.asyncio
async def test_readme_usage_example() -> None:
    crypto = AgeMreCrypto()

    sk1 = X25519PrivateKey.generate()
    pk1 = sk1.public_key()
    sk2 = X25519PrivateKey.generate()
    pk2 = sk2.public_key()

    recipients = [
        {"kind": "cryptography_obj", "obj": pk1},
        {"kind": "cryptography_obj", "obj": pk2},
    ]

    env = await crypto.encrypt_for_many(recipients, b"secret")
    pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk1}, env)
    assert pt == b"secret"
