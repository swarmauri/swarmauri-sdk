import asyncio

from swarmauri_signing_hmac import HmacEnvelopeSigner


async def _sign_and_verify() -> bool:
    signer = HmacEnvelopeSigner()
    key = {"kind": "raw", "key": "secret"}
    payload = b"unit-test"
    sigs = await signer.sign_bytes(key, payload, alg="HS256")
    ok = await signer.verify_bytes(payload, sigs, opts={"keys": [key]})
    return ok


def test_sign_and_verify_unit():
    assert asyncio.run(_sign_and_verify())
