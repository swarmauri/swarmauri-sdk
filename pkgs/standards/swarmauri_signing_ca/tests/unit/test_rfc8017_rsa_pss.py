"""RFC 8017 RSA-PSS signature tests."""

import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"rfc8017"
    sigs = await signer.sign_bytes(key, payload, alg="PS256")
    pk = sk.public_key()
    return await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})


def test_rfc8017_rsa_pss():
    assert asyncio.run(_run())
