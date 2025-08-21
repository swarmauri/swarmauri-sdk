import asyncio

import pytest


async def _tamper(service):
    token = await service.mint({"msg": "hi"}, alg="v4.public", kid="ed1")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(ValueError):
        await service.verify(tampered)


async def _aud_success(service):
    token = await service.mint({}, alg="v4.public", kid="ed1", audience=["app"])
    claims = await service.verify(token, audience="app")
    return claims.get("aud") == ["app"]


def test_tamper_detection(token_service):
    asyncio.run(_tamper(token_service))


def test_audience_success(token_service):
    assert asyncio.run(_aud_success(token_service))
