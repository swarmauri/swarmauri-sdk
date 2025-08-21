"""RFC 8032 - Ed25519 signature scheme."""

import asyncio
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = Ed25519PrivateKey.generate()
    key = SimpleNamespace(tags={"crypto_obj": sk})
    msg = b"RFC8032"
    sigs = await signer.sign_bytes(key, msg, alg="Ed25519")
    pk = sk.public_key()
    return await signer.verify_bytes(msg, sigs, opts={"pubkeys": [pk]})


def test_rfc8032_compliance():
    assert asyncio.run(_run())
