import asyncio
from swarmauri_signing_hmac import HmacEnvelopeSigner
from swarmauri_core.crypto.types import JWAAlg


async def main() -> None:
    signer = HmacEnvelopeSigner()

    # KeyRef with a raw 32-byte secret; see swarmauri_core for more options
    key = {"kind": "raw", "key": "a" * 32}

    # Sign and verify raw bytes
    payload = b"hello"
    sigs = await signer.sign_bytes(
        key, payload, alg=JWAAlg.HS256, opts={"tag_size": 16}
    )
    assert await signer.verify_bytes(payload, sigs, opts={"keys": [key]})

    # Sign and verify a JSON envelope
    env = {"msg": "hello"}
    sigs_env = await signer.sign_envelope(
        key, env, alg=JWAAlg.HS256, canon="json", opts={"tag_size": 16}
    )
    assert await signer.verify_envelope(
        env, sigs_env, canon="json", opts={"keys": [key]}
    )


asyncio.run(main())
