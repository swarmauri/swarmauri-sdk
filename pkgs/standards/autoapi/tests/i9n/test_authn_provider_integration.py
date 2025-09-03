from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from autoapi.v3.engine.shortcuts import mem
from uuid import uuid4

from autoapi.v3 import AutoApp, Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.config import __autoapi_auth_context__
from autoapi.v3.types.authn_abc import AuthNProvider


class HookedAuth(AuthNProvider):
    """Simple AuthN provider that records context via API hooks."""

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
        setattr(request.state, __autoapi_auth_context__, principal)
        return principal


def _build_client_with_auth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"

    auth = HookedAuth()

    async def _capture(ctx):
        auth.ctx_principal = ctx.get("auth")

    api = AutoApp(engine=mem(async_=False), api_hooks={"PRE_HANDLER": [_capture]})
    api.set_auth(authn=auth.get_principal)
    api.include_model(Tenant)
    api.initialize()
    return TestClient(api), auth


def test_authn_hooks_and_context_injection():
    client, auth = _build_client_with_auth()

    payload = {"id": str(uuid4())}
    res = client.post(
        "/tenant", json=payload, headers={"Authorization": "Bearer secret"}
    )
    assert res.status_code == 201
    assert auth.ctx_principal == {
        "sub": "user",
        "tid": "tenant",
        "user_id": "user",
        "tenant_id": "tenant",
    }


def test_authn_unauthorized_errors():
    client, _ = _build_client_with_auth()

    assert client.get("/tenant").status_code == 403
    assert (
        client.get("/tenant", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
