from contextlib import contextmanager

from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from autoapi.v3.autoapp import AutoApp
from autoapi.v3.engine import resolver
from autoapi.v3.engine.shortcuts import mem
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    AllowAnonProvider,
    App,
    AuthNProvider,
    Column,
    ForeignKey,
    HTTPException,
    PgUUID,
    Request,
    Security,
    String,
    uuid4,
)

from typing import Any


class DummyAuth(AuthNProvider):
    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Security(
            HTTPBearer(auto_error=False)
        ),
    ):
        if creds is None:
            if request.method == "GET":
                return None
            raise HTTPException(status_code=409)
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
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_allow_anon__(cls):
            return {"list", "read"}

    auth = DummyAuth()
    api = AutoApp(engine=mem(async_=False))
    api.set_auth(authn=auth.get_principal)
    auth.register_inject_hook(api)
    api.include_models([Tenant, Item])
    api.initialize_sync()
    app = App()
    app.include_router(api.router)
    provider = resolver.resolve_provider()

    @contextmanager
    def session() -> Any:
        db = provider.session()
        try:
            yield db
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    return TestClient(app), session, Tenant, Item


def _build_client_attr():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        __autoapi_allow_anon__ = {"list", "read"}

    auth = DummyAuth()
    api = AutoApp(engine=mem(async_=False))
    api.set_auth(authn=auth.get_principal)
    auth.register_inject_hook(api)
    api.include_models([Tenant, Item])
    api.initialize_sync()
    app = App()
    app.include_router(api.router)
    provider = resolver.resolve_provider()

    @contextmanager
    def session() -> Any:
        db = provider.session()
        try:
            yield db
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    return TestClient(app), session, Tenant, Item


def test_allow_anon_list_and_read():
    client, session, Tenant, Item = _build_client()
    with session() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        item = Item(id=uuid4(), tenant_id=tenant.id, name="thing")
        db.add(item)
        db.commit()
        db.refresh(item)
        tid = str(tenant.id)
        iid = str(item.id)
    assert client.get("/item").status_code == 200
    assert client.get(f"/item/{iid}").status_code == 200
    # Requests without credentials are rejected for non-whitelisted routes.
    payload = {"id": str(uuid4()), "tenant_id": tid, "name": "new"}
    assert client.post("/item", json=payload).status_code == 409


def test_openapi_marks_anon_and_protected_routes():
    client, session, Tenant, Item = _build_client()
    spec = client.get("/openapi.json").json()
    anon_op = spec["paths"]["/item"]["get"].get("security")
    protected_op = spec["paths"]["/item"]["post"].get("security")
    assert anon_op in (None, [])
    assert protected_op == [{"HTTPBearer": []}]
    assert "HTTPBearer" in spec["components"]["securitySchemes"]


def _build_client_create_noauth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, AllowAnonProvider):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_allow_anon__(cls):
            return {"create"}

    api = AutoApp(engine=mem(async_=False))
    api.include_models([Tenant, Item])
    api.initialize_sync()
    app = App()
    app.include_router(api.router)
    provider = resolver.resolve_provider()

    @contextmanager
    def session() -> Any:
        db = provider.session()
        try:
            yield db
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    return TestClient(app), session, Tenant, Item


def _build_client_create_attr_noauth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, AllowAnonProvider):
        __tablename__ = "items"
        tenant_id = Column(
            PgUUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
        )
        name = Column(String, nullable=False)

        __autoapi_allow_anon__ = {"create"}

    api = AutoApp(engine=mem(async_=False))
    api.include_models([Tenant, Item])
    api.initialize_sync()
    app = App()
    app.include_router(api.router)
    provider = resolver.resolve_provider()

    @contextmanager
    def session() -> Any:
        db = provider.session()
        try:
            yield db
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    return TestClient(app), session, Tenant, Item


def test_allow_anon_create_method():
    client, session, Tenant, Item = _build_client_create_noauth()
    with session() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        payload = {"id": str(uuid4()), "tenant_id": str(tenant.id), "name": "thing"}
    assert client.post("/item", json=payload).status_code == 201


def test_allow_anon_create_attr_noauth():
    client, session, Tenant, Item = _build_client_create_attr_noauth()
    with session() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        payload = {"id": str(uuid4()), "tenant_id": str(tenant.id), "name": "thing"}
    assert client.post("/item", json=payload).status_code == 201


def test_allow_anon_list_and_read_attr():
    client, session, Tenant, Item = _build_client_attr()
    with session() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        item = Item(id=uuid4(), tenant_id=tenant.id, name="thing")
        db.add(item)
        db.commit()
        db.refresh(item)
        tid = str(tenant.id)
        iid = str(item.id)
    assert client.get("/item").status_code == 200
    assert client.get(f"/item/{iid}").status_code == 200
    payload = {"id": str(uuid4()), "tenant_id": tid, "name": "new"}
    assert client.post("/item", json=payload).status_code == 409
