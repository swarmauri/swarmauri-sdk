import asyncio
import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_hmac import HmacEnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "a" * 32}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload, alg=JWAAlg.HS256)
    ok = await signer.verify_bytes(payload, sigs, opts={"keys": [key]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())


def test_key_too_short_raises():
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "short"}
    with pytest.raises(ValueError):
        asyncio.run(signer.sign_bytes(key, b"payload"))


async def _truncated_ok() -> bool:
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "a" * 32}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(
        key, payload, alg=JWAAlg.HS256, opts={"tag_size": 16}
    )
    return await signer.verify_bytes(payload, sigs, opts={"keys": [key]})


def test_truncated_tag_verify():
    assert asyncio.run(_truncated_ok())


def test_tag_too_short():
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "a" * 32}
    with pytest.raises(ValueError):
        asyncio.run(
            signer.sign_bytes(key, b"payload", alg=JWAAlg.HS256, opts={"tag_size": 8})
        )


def test_verify_rejects_short_sig():
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "a" * 32}
    payload = b"unit-test"
    sigs = asyncio.run(
        signer.sign_bytes(key, payload, alg=JWAAlg.HS256, opts={"tag_size": 16})
    )
    sigs[0].data["sig"] = sigs[0].data["sig"][:10]
    ok = asyncio.run(signer.verify_bytes(payload, sigs, opts={"keys": [key]}))
    assert not ok
