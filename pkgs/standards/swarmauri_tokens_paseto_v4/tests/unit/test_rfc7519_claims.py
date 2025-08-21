import asyncio
import time

import pytest


async def _expired(service):
    token = await service.mint(
        {"exp": int(time.time()) - 1000}, alg="v4.public", kid="ed1", lifetime_s=None
    )
    with pytest.raises(ValueError):
        await service.verify(token, leeway_s=0)


async def _issuer_mismatch(service):
    token = await service.mint({}, alg="v4.public", kid="ed1", issuer="issuer")
    with pytest.raises(ValueError):
        await service.verify(token, issuer="other")


async def _audience_mismatch(service):
    token = await service.mint({}, alg="v4.public", kid="ed1", audience="me")
    with pytest.raises(ValueError):
        await service.verify(token, audience="you")


def test_expired_claim(token_service):
    asyncio.run(_expired(token_service))


def test_issuer_mismatch(token_service):
    asyncio.run(_issuer_mismatch(token_service))


def test_audience_mismatch(token_service):
    asyncio.run(_audience_mismatch(token_service))
