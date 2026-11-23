"""Exercises the README usage example to prevent regressions."""

import pytest

from swarmauri_signing_hmac import HmacEnvelopeSigner
from swarmauri_core.crypto.types import JWAAlg


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_usage_example() -> None:
    signer = HmacEnvelopeSigner()

    key = {"kind": "raw", "key": "a" * 32}
    payload = b"hello"

    sigs = await signer.sign_bytes(
        key, payload, alg=JWAAlg.HS256, opts={"tag_size": 16}
    )
    assert await signer.verify_bytes(payload, sigs, opts={"keys": [key]})

    env = {"msg": "hello"}
    sigs_env = await signer.sign_envelope(
        key, env, alg=JWAAlg.HS256, canon="json", opts={"tag_size": 16}
    )

    assert await signer.verify_envelope(
        env, sigs_env, canon="json", opts={"keys": [key]}
    )
