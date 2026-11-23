import asyncio

import pytest

from swarmauri_tokens_composite import CompositeTokenService


class DummyService:
    type = "JWTTokenService"

    def __init__(self):
        self._formats = ["JWT"]
        self._algs = ["HS256"]

    def supports(self):
        return {"formats": self._formats, "algs": self._algs}

    async def mint(self, claims, *, alg, **kwargs):
        return "token"

    async def verify(self, token, **kwargs):  # pragma: no cover - unused
        return {"token": token}

    async def jwks(self):  # pragma: no cover - unused
        return {"keys": []}


@pytest.mark.perf
def test_mint_performance(benchmark):
    svc = DummyService()
    comp = CompositeTokenService([svc])

    async def do_mint():
        await comp.mint({}, alg="HS256")

    benchmark(lambda: asyncio.run(do_mint()))
