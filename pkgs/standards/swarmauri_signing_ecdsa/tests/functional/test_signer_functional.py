import asyncio
from cryptography.hazmat.primitives.asymmetric import ec

from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = EcdsaEnvelopeSigner()
    sk = ec.generate_private_key(ec.SECP256R1())
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
