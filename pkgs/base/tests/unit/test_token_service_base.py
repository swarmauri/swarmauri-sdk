import pytest

from swarmauri_base.tokens import TokenServiceBase
from swarmauri_base.ComponentBase import ResourceTypes


class DummyTokenService(TokenServiceBase):
    def supports(self):
        return {"formats": (), "algs": ()}

    async def mint(
        self,
        claims,
        *,
        alg,
        kid=None,
        key_version=None,
        headers=None,
        lifetime_s=3600,
        issuer=None,
        subject=None,
        audience=None,
        scope=None,
    ):
        return ""

    async def verify(self, token, *, issuer=None, audience=None, leeway_s=60):
        return {}

    async def jwks(self) -> dict:
        return {}


@pytest.mark.unit
def test_base_defaults() -> None:
    svc = DummyTokenService()
    assert svc.resource == ResourceTypes.CRYPTO.value
    assert svc.type == "DummyTokenService"
