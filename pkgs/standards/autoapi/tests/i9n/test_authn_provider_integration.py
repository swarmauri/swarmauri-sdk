from autoapi.v3.types import App, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.types.authn_abc import AuthNProvider

AUTH_CONTEXT_KEY = "auth_context"


class HookedAuth(AuthNProvider):
    """Simple AuthN provider that records context via a hook."""

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
        request.state.auth_context = principal
        return principal

    def register_inject_hook(self, api) -> None:  # pragma: no cover - runtime wiring
        async def _capture(ctx):  # pragma: no cover - executed in tests
            ctx[AUTH_CONTEXT_KEY] = getattr(
                ctx.get("request").state, AUTH_CONTEXT_KEY, None
            )
            self.ctx_principal = ctx.get(AUTH_CONTEXT_KEY)

        hooks = getattr(api, "_api_hooks_map", {}) or {}
        hooks.setdefault("PRE_HANDLER", []).append(_capture)
        api._api_hooks_map = hooks


def _build_client_with_auth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    auth = HookedAuth()
    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.set_auth(authn=auth.get_principal)
    auth.register_inject_hook(api)
    api.include_model(Tenant)
    api.initialize_sync()
    return TestClient(app), auth


def test_authn_hooks_and_context_injection():
    client, auth = _build_client_with_auth()

    payload = {"id": str(uuid4())}
    res = client.post(
        "/tenant", json=payload, headers={"Authorization": "Bearer secret"}
    )
    assert res.status_code == 201
    assert auth.ctx_principal == {"sub": "user", "tid": "tenant"}


def test_authn_unauthorized_errors():
    client, _ = _build_client_with_auth()

    assert client.get("/tenant").status_code == 403
    assert (
        client.get("/tenant", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
