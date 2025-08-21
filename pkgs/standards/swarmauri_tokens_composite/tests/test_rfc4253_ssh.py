"""Tests referencing RFC 4253 for SSH certificates."""

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

    async def mint(self, claims, *, alg, **kwargs):  # pragma: no cover - unused
        return "tok"

    async def verify(self, token, **kwargs):  # pragma: no cover - unused
        return {"service": self.name}

    async def jwks(self):  # pragma: no cover - unused
        return {"keys": []}


@pytest.mark.test
@pytest.mark.unit
def test_rfc4253_ssh_cert_routing():
    ssh_service = DummyService("SSHService", ["SSH-CERT"], ["ssh-ed25519"])
    jwt_service = DummyService("JWTTokenService", ["JWT"], ["HS256"])
    comp = CompositeTokenService([ssh_service, jwt_service])
    svc = comp._select_service_for_verify("ssh-ed25519-cert-v01@openssh.com AAAA")
    assert svc is ssh_service
