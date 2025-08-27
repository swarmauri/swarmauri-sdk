from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy import Column, ForeignKey, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types.authn_abc import AuthNProvider

AUTH_CONTEXT_KEY = "auth_context"


class HookedAuth(AuthNProvider):
    """Simple AuthN provider that records context via a hook."""

    def __init__(self) -> None:
        self.ctx_principal: dict | None = None

    async def get_principal(
        self,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> dict:
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        return {"sub": "user", "tid": "tenant"}

    def register_inject_hook(self, api) -> None:  # pragma: no cover - runtime wiring
        @api.register_hook("PRE_TX_BEGIN")
        async def _capture(ctx):  # pragma: no cover - executed in tests
            self.ctx_principal = ctx.get(AUTH_CONTEXT_KEY)


def _build_client_with_auth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

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
    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db, authn=auth)
    auth.register_inject_hook(api)
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app), auth


def test_authn_hooks_and_context_injection():
    client, auth = _build_client_with_auth()

    tenant = {"name": "acme"}
    res = client.post(
        "/tenant", json=tenant, headers={"Authorization": "Bearer secret"}
    )
    tid = res.json()["id"]

    auth.ctx_principal = None
    payload = {"tenant_id": tid, "name": "widget"}
    res = client.post("/item", json=payload, headers={"Authorization": "Bearer secret"})
    assert res.status_code == 201
    assert auth.ctx_principal == {"sub": "user", "tid": "tenant"}


def test_authn_unauthorized_errors():
    client, _ = _build_client_with_auth()

    assert client.get("/item").status_code == 403
    assert (
        client.get("/item", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
