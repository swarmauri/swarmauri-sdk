import pytest
from swarmauri_core.tokens import ITokenService


class DummyTokenService(ITokenService):
    def supports(self):
        return {"formats": ("JWT",), "algs": ("HS256",)}

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
        return "token"

    async def verify(self, token, *, issuer=None, audience=None, leeway_s=60):
        return {}

    async def jwks(self) -> dict:
        return {}


@pytest.mark.unit
def test_itokenservice_is_abstract() -> None:
    with pytest.raises(TypeError):
        ITokenService()


@pytest.mark.unit
def test_subclass_supports() -> None:
    svc = DummyTokenService()
    assert "JWT" in svc.supports()["formats"]
