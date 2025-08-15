from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.mixins.ownable import Ownable, OwnerPolicy
from autoapi.v3.mixins.tenant_bound import TenantBound, TenantPolicy
from autoapi.v3.types import AuthNProvider
from autoapi.v3.hooks import Phase


class DummyAuth(AuthNProvider):
    def __init__(self, user_id: uuid.UUID, tenant_id: uuid.UUID):
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def get_principal(
        self, creds: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ):
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        return {"user_id": self.user_id, "tenant_id": self.tenant_id}

    def register_inject_hook(self, api) -> None:
        @api.register_hook(Phase.PRE_TX_BEGIN)
        async def _inject(ctx):
            p = getattr(ctx["request"].state, "principal", None)
            if not p:
                return
            injected = ctx.setdefault("__autoapi_injected_fields__", {})
            if p.get("tenant_id") is not None:
                injected["tenant_id"] = p["tenant_id"]
            if p.get("user_id") is not None:
                injected["user_id"] = p["user_id"]


def _client_for_owner(
    policy: OwnerPolicy, user_id: uuid.UUID, tenant_id: uuid.UUID
) -> TestClient:
    Base.metadata.clear()

    class User(Base, GUIDPk):
        __tablename__ = "users"
        __table_args__ = {"schema": "main"}
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, Ownable):
        __tablename__ = "items"
        __table_args__ = {"schema": "main"}
        name = Column(String, nullable=False)
        __autoapi_owner_policy__ = policy

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.execute(User.__table__.insert().values(id=user_id, name="owner"))
        session.commit()

    def get_db():
        with SessionLocal() as session:
            yield session

    authn = DummyAuth(user_id, tenant_id)
    api = AutoAPI(base=Base, include={User, Item}, get_db=get_db, authn=authn)
    authn.register_inject_hook(api)
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


def test_owner_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_owner(OwnerPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post("/item", json={"name": "one"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["owner_id"] == str(user_id)

    client = _client_for_owner(OwnerPolicy.CLIENT_SET, user_id, tenant_id)
    supplied = str(uuid.uuid4())
    res = client.post(
        "/item", json={"name": "two", "owner_id": supplied}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["owner_id"] == supplied


def _client_for_tenant(
    policy: TenantPolicy, user_id: uuid.UUID, tenant_id: uuid.UUID
) -> TestClient:
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        __table_args__ = {"schema": "main"}
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, TenantBound):
        __tablename__ = "items"
        __table_args__ = {"schema": "main"}
        name = Column(String, nullable=False)
        __autoapi_tenant_policy__ = policy

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.execute(Tenant.__table__.insert().values(id=tenant_id, name="acme"))
        session.commit()

    def get_db():
        with SessionLocal() as session:
            yield session

    authn = DummyAuth(user_id, tenant_id)
    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db, authn=authn)
    authn.register_inject_hook(api)
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


def test_tenant_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_tenant(TenantPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post("/item", json={"name": "one"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["tenant_id"] == str(tenant_id)

    client = _client_for_tenant(TenantPolicy.CLIENT_SET, user_id, tenant_id)
    supplied = str(uuid.uuid4())
    res = client.post(
        "/item", json={"name": "two", "tenant_id": supplied}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["tenant_id"] == supplied
