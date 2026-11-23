import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner


async def main() -> bool:
    signer = Ed25519EnvelopeSigner()
    private_key = Ed25519PrivateKey.generate()
    key_ref = {"kind": "cryptography_obj", "obj": private_key}

    envelope = {"subject": "alice", "scope": ["inbox:read"]}
    signatures = await signer.sign_envelope(key_ref, envelope)

    public_key = private_key.public_key()
    verified = await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [public_key]},
    )
    return verified


verified = asyncio.run(main())
print(f"Signature verified? {verified}")
