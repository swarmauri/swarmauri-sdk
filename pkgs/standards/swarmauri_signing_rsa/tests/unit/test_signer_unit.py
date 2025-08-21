import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_rsa import RSAEnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = RSAEnvelopeSigner()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = {"kind": "cryptography_obj", "obj": sk}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload)
    pk = sk.public_key()
    ok = await signer.verify_bytes(
        payload, sigs, opts={"pubkeys": [{"kind": "cryptography_obj", "obj": pk}]}
    )
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
