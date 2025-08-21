import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = EcdsaEnvelopeSigner()
    sk = ec.generate_private_key(ec.SECP256R1())
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pk]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
