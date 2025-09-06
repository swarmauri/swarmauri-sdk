from autoapi.v3.types import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from autoapi.v3.engine.shortcuts import mem

from autoapi.v3 import AutoApp, Base, hook_ctx
from autoapi.v3.config.constants import AUTOAPI_AUTH_CONTEXT_ATTR
from autoapi.v3.orm.mixins import GUIDPk, BulkCapable
from autoapi.v3.types.authn_abc import AuthNProvider


class HookedAuth(AuthNProvider):
    """Simple AuthN provider that records context via hooks."""

    def __init__(self) -> None:
        self.ctx_principal: dict | None = None

    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> dict:
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        principal = {"sub": "user", "tid": "tenant"}
        setattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, principal)
        return principal


def _build_client_with_auth():
    Base.metadata.clear()

    auth = HookedAuth()

    class Tenant(Base, GUIDPk, BulkCapable):
        __tablename__ = "tenants"

        @hook_ctx(ops="bulk_create", phase="PRE_HANDLER")
        async def capture(cls, ctx):
            auth.ctx_principal = ctx.get("auth_context")

    api = AutoApp(engine=mem(async_=False))
    api.set_auth(authn=auth.get_principal)
    api.include_model(Tenant)
    api.initialize()
    return TestClient(api), auth


def test_authn_hooks_and_context_injection():
    client, auth = _build_client_with_auth()

    res = client.post("/tenant", json=[{}], headers={"Authorization": "Bearer secret"})
    assert res.status_code == 201
    assert auth.ctx_principal == {"sub": "user", "tid": "tenant"}


def test_authn_unauthorized_errors():
    client, _ = _build_client_with_auth()

    assert client.get("/tenant").status_code == 403
    assert (
        client.get("/tenant", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
