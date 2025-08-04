from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Column, String, ForeignKey, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker

from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import GUIDPk
from autoapi.v2.types import AuthNProvider
from fastapi import Request


class DummyAuth(AuthNProvider):
    async def get_principal(self, request: Request):
        if request.headers.get("Authorization") != "Bearer secret":
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


def test_allow_anon_list_and_read():
    client = _build_client()
    assert client.get("/items").status_code == 200
    tenant = {"name": "acme"}
    res = client.post(
        "/tenants", json=tenant, headers={"Authorization": "Bearer secret"}
    )
    tid = res.json()["id"]
    payload = {"tenant_id": tid, "name": "thing"}
    res = client.post(
        "/items", json=payload, headers={"Authorization": "Bearer secret"}
    )
    iid = res.json()["id"]
    assert client.get(f"/items/{iid}").status_code == 200
    assert client.post("/items", json=payload).status_code == 401
