"""Tests referencing RFC 7519 (JWT)."""

import pytest

from swarmauri_tokens_composite import CompositeTokenService


class DummyService:
    def __init__(self, name, formats, algs):
        self.name = name
        self.type = name
        self._formats = formats
        self._algs = algs

    def supports(self):
        return {"formats": self._formats, "algs": self._algs}

    async def mint(self, claims, *, alg, **kwargs):
        return f"{self.name}:{alg}"

    async def verify(self, token, **kwargs):  # pragma: no cover - unused
        return {"service": self.name}

    async def jwks(self):  # pragma: no cover - unused
        return {"keys": []}


@pytest.mark.test
@pytest.mark.unit
@pytest.mark.asyncio
async def test_rfc7519_typ_header_routes_jwt():
    jwt_service = DummyService("JWTTokenService", ["JWT"], ["HS256"])
    ssh_service = DummyService("SSHService", ["SSH-CERT"], ["ssh-ed25519"])
    comp = CompositeTokenService([jwt_service, ssh_service])
    tok = await comp.mint({}, alg="HS256", headers={"typ": "JWT"})
    assert tok.startswith("JWTTokenService")
