import pytest

from swarmauri_tokens_composite import CompositeTokenService


class DummyService:
    type = "JWTTokenService"

    def __init__(self, name: str, formats, algs, fail=False):
        self.name = name
        self._formats = formats
        self._algs = algs
        self.fail = fail

    def supports(self):
        return {"formats": self._formats, "algs": self._algs}

    async def mint(self, claims, *, alg, **kwargs):  # pragma: no cover - unused
        return f"{self.name}:{alg}"

    async def verify(self, token, **kwargs):
        if self.fail:
            raise ValueError("fail")
        return {"token": token, "service": self.name}

    async def jwks(self):  # pragma: no cover - unused
        return {"keys": []}


@pytest.mark.test
@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_verify_fallback():
    failing = DummyService("bad", ["JWT"], ["HS256"], fail=True)
    good = DummyService("good", ["JWT"], ["HS256"])
    comp = CompositeTokenService([failing, good])
    res = await comp.verify("a.b.c")
    assert res["service"] == "good"
