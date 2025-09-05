import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_ca import CASigner


async def _sign_and_verify() -> bool:
    signer = CASigner()
    sk = ed25519.Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
