from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from sqlalchemy.orm import sessionmaker

from tigrbl import TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from tigrbl.types import (
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
        principal = {"sub": "user"}
        setattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, principal)
        return principal


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
        def __tigrbl_allow_anon__(cls):
            return {"list", "read"}

    cfg = mem(async_=False)
    auth = DummyAuth()
    api = TigrblApp(engine=cfg)
    api.set_auth(authn=auth.get_principal)
    api.include_models([Tenant, Item])
    api.initialize()
    app = App()
    app.include_router(api.router)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    client = TestClient(app)
    return client, SessionLocal, Tenant, Item


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

        __tigrbl_allow_anon__ = {"list", "read"}

    cfg = mem(async_=False)
    auth = DummyAuth()
    api = TigrblApp(engine=cfg)
    api.set_auth(authn=auth.get_principal)
    api.include_models([Tenant, Item])
    api.initialize()
    app = App()
    app.include_router(api.router)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    client = TestClient(app)
    return client, SessionLocal, Tenant, Item


def test_allow_anon_list_and_read():
    client, SessionLocal, Tenant, Item = _build_client()
    with SessionLocal() as db:
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
    client, SessionLocal, Tenant, Item = _build_client()
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
        def __tigrbl_allow_anon__(cls):
            return {"create", "bulk_create"}

    cfg = mem(async_=False)
    api = TigrblApp(engine=cfg)
    api.include_models([Tenant, Item])
    api.initialize()
    app = App()
    app.include_router(api.router)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    client = TestClient(app)
    return client, SessionLocal, Tenant, Item


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

        __tigrbl_allow_anon__ = {"create", "bulk_create"}

    cfg = mem(async_=False)
    api = TigrblApp(engine=cfg)
    api.include_models([Tenant, Item])
    api.initialize()
    app = App()
    app.include_router(api.router)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    client = TestClient(app)
    return client, SessionLocal, Tenant, Item


def test_allow_anon_create_method():
    client, SessionLocal, Tenant, Item = _build_client_create_noauth()
    with SessionLocal() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        tid = str(tenant.id)
    payload = {"id": str(uuid4()), "tenant_id": tid, "name": "one"}
    assert client.post("/item", json=[payload]).status_code == 201


def test_allow_anon_create_attr_noauth():
    client, SessionLocal, Tenant, Item = _build_client_create_attr_noauth()
    with SessionLocal() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        tid = str(tenant.id)
    payload = {"id": str(uuid4()), "tenant_id": tid, "name": "one"}
    assert client.post("/item", json=[payload]).status_code == 201


def test_allow_anon_list_and_read_attr():
    client, SessionLocal, Tenant, Item = _build_client_attr()
    with SessionLocal() as db:
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
