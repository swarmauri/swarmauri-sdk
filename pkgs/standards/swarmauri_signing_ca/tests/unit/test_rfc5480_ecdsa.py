"""RFC 5480 ECDSA P-256 signature tests."""

import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ca import CASigner


async def _run() -> bool:
    signer = CASigner()
    sk = ec.generate_private_key(ec.SECP256R1())
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"rfc5480"
    sigs = await signer.sign_bytes(key, payload, alg="ECDSA-P256-SHA256")
    pk = sk.public_key()
    return await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})


def test_rfc5480_ecdsa():
    assert asyncio.run(_run())
