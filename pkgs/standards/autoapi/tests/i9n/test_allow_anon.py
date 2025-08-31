from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.tables import Base
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
from autoapi.v3.config import __autoapi_auth_context__


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
        request.state.principal = principal
        setattr(request.state, __autoapi_auth_context__, principal)
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

    auth = DummyAuth()
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=auth.get_principal)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app), SessionLocal, Tenant, Item


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

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    auth = DummyAuth()
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=auth.get_principal)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app), SessionLocal, Tenant, Item


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
        def __autoapi_allow_anon__(cls):
            return {"create"}

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(get_db=get_db)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app), SessionLocal, Tenant, Item


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

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(get_db=get_db)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app), SessionLocal, Tenant, Item


def test_allow_anon_create_method():
    client, SessionLocal, Tenant, Item = _build_client_create_noauth()
    with SessionLocal() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        payload = {"id": str(uuid4()), "tenant_id": str(tenant.id), "name": "thing"}
    assert client.post("/item", json=payload).status_code == 201


def test_allow_anon_create_attr_noauth():
    client, SessionLocal, Tenant, Item = _build_client_create_attr_noauth()
    with SessionLocal() as db:
        tenant = Tenant(id=uuid4(), name="acme")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        payload = {"id": str(uuid4()), "tenant_id": str(tenant.id), "name": "thing"}
    assert client.post("/item", json=payload).status_code == 201


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
