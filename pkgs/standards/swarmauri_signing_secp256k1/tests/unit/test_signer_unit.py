import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = Secp256k1EnvelopeSigner()
    sk = ec.generate_private_key(ec.SECP256K1())
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})
    return ok


def test_sign_and_verify_unit() -> None:
    assert asyncio.run(_sign_and_verify())
