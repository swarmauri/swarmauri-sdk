"""RFC 8017 - RSA Probabilistic Signature Scheme (RSASSA-PSS)."""

import asyncio
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = SimpleNamespace(tags={"crypto_obj": sk})
    msg = b"RFC8017"
    sigs = await signer.sign_bytes(key, msg, alg="RSA-PSS-SHA256")
    pk = sk.public_key()
    return await signer.verify_bytes(msg, sigs, opts={"pubkeys": [pk]})


def test_rfc8017_compliance():
    assert asyncio.run(_run())
