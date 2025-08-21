"""RFC 6979 - Deterministic ECDSA using P-256."""

import asyncio
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = ec.generate_private_key(ec.SECP256R1())
    key = SimpleNamespace(tags={"crypto_obj": sk})
    msg = b"RFC6979"
    sigs = await signer.sign_bytes(key, msg, alg="ECDSA-P256-SHA256")
    pk = sk.public_key()
    return await signer.verify_bytes(msg, sigs, opts={"pubkeys": [pk]})


def test_rfc6979_compliance():
    assert asyncio.run(_run())
