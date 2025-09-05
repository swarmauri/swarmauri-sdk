import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = Ed25519EnvelopeSigner()
    sk = Ed25519PrivateKey.generate()
    key = {"kind": "cryptography_obj", "obj": sk}
    env = create_env("hello")
    sigs = await signer.sign_envelope(key, env, canon="json")
    pk = sk.public_key()
    good = await signer.verify_envelope(env, sigs, canon="json", opts={"pubkeys": [pk]})
    bad = await signer.verify_envelope(
        {"msg": "tampered"}, sigs, canon="json", opts={"pubkeys": [pk]}
    )
    return good and not bad


def test_sign_and_verify_envelope_functional():
    assert asyncio.run(_run())
