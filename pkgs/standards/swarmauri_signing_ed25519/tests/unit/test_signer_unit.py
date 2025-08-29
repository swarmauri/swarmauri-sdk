import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = Ed25519EnvelopeSigner()
    sk = Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
