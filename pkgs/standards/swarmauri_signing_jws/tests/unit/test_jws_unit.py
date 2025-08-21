import asyncio

from swarmauri_signing_jws import JwsSignerVerifier


async def _sign_and_verify() -> bool:
    jws = JwsSignerVerifier()
    key = {"kind": "raw", "key": "secret"}
    token = await jws.sign_compact(payload={"msg": "unit"}, alg="HS256", key=key)
    res = await jws.verify_compact(token, hmac_keys=[key])
    return res.payload == b'{"msg":"unit"}'


def test_jws_sign_verify_unit() -> None:
    assert asyncio.run(_sign_and_verify())
