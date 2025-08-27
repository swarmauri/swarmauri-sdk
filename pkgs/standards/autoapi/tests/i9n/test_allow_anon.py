from fastapi import FastAPI, HTTPException, Security
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Column, ForeignKey, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types.authn_abc import AuthNProvider


class DummyAuth(AuthNProvider):
    async def get_principal(
        self,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ):
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        return {"sub": "user"}

    def register_inject_hook(self, api) -> None:
        return None


def _build_client():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_allow_anon__(cls):
            return {"list", "read"}

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db, authn=DummyAuth())
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


def _build_client_attr():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

        __autoapi_allow_anon__ = {"list", "read"}

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db, authn=DummyAuth())
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


def test_allow_anon_list_and_read():
    client = _build_client()
    assert client.get("/item").status_code == 200
    tenant = {"name": "acme"}
    res = client.post(
        "/tenant", json=tenant, headers={"Authorization": "Bearer secret"}
    )
    tid = res.json()["id"]
    payload = {"tenant_id": tid, "name": "thing"}
    res = client.post("/item", json=payload, headers={"Authorization": "Bearer secret"})
    iid = res.json()["id"]
    assert client.get(f"/item/{iid}").status_code == 200
    # FastAPI's HTTPBearer returns 403 when the Authorization header is
    # completely missing (as opposed to a malformed token).  The AutoAPI
    # endpoint mirrors this behaviour for unauthenticated access to routes
    # that are not whitelisted via ``__autoapi_allow_anon__``.
    assert client.post("/item", json=payload).status_code == 403


def test_allow_anon_list_and_read_attr():
    client = _build_client_attr()
    assert client.get("/item").status_code == 200
    tenant = {"name": "acme"}
    res = client.post(
        "/tenant", json=tenant, headers={"Authorization": "Bearer secret"}
    )
    tid = res.json()["id"]
    payload = {"tenant_id": tid, "name": "thing"}
    res = client.post("/item", json=payload, headers={"Authorization": "Bearer secret"})
    iid = res.json()["id"]
    assert client.get(f"/item/{iid}").status_code == 200
    assert client.post("/item", json=payload).status_code == 403
