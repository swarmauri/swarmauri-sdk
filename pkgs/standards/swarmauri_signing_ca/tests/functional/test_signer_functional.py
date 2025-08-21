import asyncio
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from swarmauri_signing_ca import CASigner


def create_env(message: str):
    return {"msg": message}


async def _run() -> bool:
    signer = CASigner()
    sk = ed25519.Ed25519PrivateKey.generate()
    key = SimpleNamespace(tags={"crypto_obj": sk})
    env = create_env("hello")
    sigs = await signer.sign_envelope(key, env, canon="json")
    pk = sk.public_key()
    good = await signer.verify_envelope(env, sigs, canon="json", opts={"pubkeys": [pk]})
    bad = await signer.verify_envelope(
        {"msg": "tampered"}, sigs, canon="json", opts={"pubkeys": [pk]}
    )

    ca_key = SimpleNamespace(
        tags={
            "crypto_obj": rsa.generate_private_key(public_exponent=65537, key_size=2048)
        }
    )
    ca_cert = signer.issue_self_signed(ca_key, {"C": "US", "O": "Test", "CN": "Root"})
    leaf_key = SimpleNamespace(
        tags={
            "crypto_obj": rsa.generate_private_key(public_exponent=65537, key_size=2048)
        }
    )
    csr = signer.create_csr({"C": "US", "O": "Test", "CN": "Leaf"}, leaf_key)
    leaf_cert = signer.sign_csr(csr, ca_key, ca_cert)
    chain_ok = signer.verify_chain(leaf_cert, roots_pems=[ca_cert])

    return good and not bad and chain_ok


def test_signer_functional():
    assert asyncio.run(_run())
