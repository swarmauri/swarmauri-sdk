import pytest

from swarmauri_tokens_composite import CompositeTokenService


class DummyService:
    type = "JWTTokenService"

    def __init__(self, name: str, formats, algs):
        self.name = name
        self._formats = formats
        self._algs = algs
        self.minted = []

    def supports(self):
        return {"formats": self._formats, "algs": self._algs}

    async def mint(self, claims, *, alg, **kwargs):
        self.minted.append((claims, alg))
        return f"{self.name}:{alg}"

    async def verify(self, token, **kwargs):  # pragma: no cover - not used here
        return {"token": token, "service": self.name}

    async def jwks(self):  # pragma: no cover - not used here
        return {"keys": [{"kid": self.name}]}


@pytest.mark.test
@pytest.mark.unit
@pytest.mark.asyncio
async def test_mint_routes_by_alg():
    s1 = DummyService("s1", ["JWT"], ["HS256"])
    s2 = DummyService("s2", ["JWT"], ["RS256"])
    comp = CompositeTokenService([s1, s2])
    tok = await comp.mint({}, alg="RS256")
    assert tok == "s2:RS256"


@pytest.mark.test
@pytest.mark.unit
@pytest.mark.asyncio
async def test_supports_merges_caps():
    s1 = DummyService("s1", ["JWT"], ["HS256"])
    s2 = DummyService("s2", ["SSH-CERT"], ["ssh-ed25519"])
    comp = CompositeTokenService([s1, s2])
    caps = comp.supports()
    assert "JWT" in caps["formats"] and "SSH-CERT" in caps["formats"]
