import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_signing_rsa import RSAEnvelopeSigner


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = RSAEnvelopeSigner()
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key = {"kind": "cryptography_obj", "obj": sk}
    env = create_env("hello")
    sigs = await signer.sign_envelope(key, env, canon="json")
    pk = sk.public_key()
    pub = {"kind": "cryptography_obj", "obj": pk}
    good = await signer.verify_envelope(
        env, sigs, canon="json", opts={"pubkeys": [pub]}
    )
    bad = await signer.verify_envelope(
        {"msg": "tampered"}, sigs, canon="json", opts={"pubkeys": [pub]}
    )
    return good and not bad


def test_sign_and_verify_envelope_functional():
    assert asyncio.run(_run())
