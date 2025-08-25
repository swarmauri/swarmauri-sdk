import asyncio

from swarmauri_signing_hmac import HmacEnvelopeSigner
from swarmauri_core.crypto.types import JWAAlg


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "secret"}
    env = create_env("hello")
    sigs = await signer.sign_envelope(key, env, alg=JWAAlg.HS256, canon="json")
    good = await signer.verify_envelope(env, sigs, canon="json", opts={"keys": [key]})
    bad = await signer.verify_envelope(
        {"msg": "tampered"}, sigs, canon="json", opts={"keys": [key]}
    )
    return good and not bad


def test_sign_and_verify_envelope_functional():
    assert asyncio.run(_run())
