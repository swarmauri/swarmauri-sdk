"""RFC 8032 Ed25519 signature tests."""

import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = ed25519.Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"rfc8032"
    sigs = await signer.sign_bytes(key, payload, alg="Ed25519")
    pk = sk.public_key()
    return await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})


def test_rfc8032_ed25519():
    assert asyncio.run(_run())
