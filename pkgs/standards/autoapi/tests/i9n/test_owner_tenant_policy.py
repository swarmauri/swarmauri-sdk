from autoapi.v3.types import App, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
import pytest
import uuid
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.mixins.ownable import Ownable, OwnerPolicy
from autoapi.v3.mixins.tenant_bound import TenantBound, TenantPolicy
from autoapi.v3.types.authn_abc import AuthNProvider


class DummyAuth(AuthNProvider):
    def __init__(self, user_id: uuid.UUID, tenant_id: uuid.UUID):
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ):
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        principal = {"user_id": self.user_id, "tenant_id": self.tenant_id}
        request.state.principal = principal
        return principal

    def register_inject_hook(self, api) -> None:
        async def _inject(ctx):
            req = (
                ctx.get("request")
                if isinstance(ctx, dict)
                else getattr(ctx, "request", None)
            )
            p = getattr(req.state, "principal", None) if req else None
            if not p:
                return
            env = ctx.get("env") if isinstance(ctx, dict) else getattr(ctx, "env", None)
            if env is not None and not isinstance(env, dict):
                params = getattr(env, "params", {})
                if isinstance(ctx, dict):
                    ctx["env"] = {"params": params}
                else:
                    setattr(ctx, "env", {"params": params})
            if isinstance(ctx, dict):
                injected = ctx.setdefault("__autoapi_injected_fields__", {})
            else:
                injected = getattr(ctx, "__autoapi_injected_fields__", {})
                if not hasattr(ctx, "__autoapi_injected_fields__"):
                    setattr(ctx, "__autoapi_injected_fields__", injected)
            if p.get("tenant_id") is not None:
                injected["tenant_id"] = p["tenant_id"]
            if p.get("user_id") is not None:
                injected["user_id"] = p["user_id"]

        hooks = getattr(api, "_api_hooks_map", {}) or {}
        hooks.setdefault("PRE_TX_BEGIN", []).append(_inject)
        api._api_hooks_map = hooks


def _client_for_owner(
    policy: OwnerPolicy, user_id: uuid.UUID, tenant_id: uuid.UUID
) -> TestClient:
    from autoapi.v2.impl import schema as v2_schema
    from autoapi.v3.schema import builder as v3_builder

    Base.metadata.clear()
    v2_schema._SchemaCache.clear()
    v3_builder._SchemaCache.clear()

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
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=authn.get_principal)
    authn.register_inject_hook(api)
    api.include_models([User, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    client = TestClient(app)
    v2_schema._SchemaCache.clear()
    v3_builder._SchemaCache.clear()
    Base.metadata.clear()
    return client


@pytest.mark.i9n
@pytest.mark.xfail(reason="Owner/Tenant policy integration currently unstable")
def test_owner_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_owner(OwnerPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post(
        "/item",
        json={"id": str(uuid.uuid4()), "name": "one", "owner_id": str(user_id)},
        headers=headers,
    )
    assert res.status_code == 400

    client = _client_for_owner(OwnerPolicy.CLIENT_SET, user_id, tenant_id)
    supplied = str(uuid.uuid4())
    res = client.post(
        "/item",
        json={"id": str(uuid.uuid4()), "name": "two", "owner_id": supplied},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["owner_id"] == supplied


def _client_for_tenant(
    policy: TenantPolicy, user_id: uuid.UUID, tenant_id: uuid.UUID
) -> TestClient:
    from autoapi.v2.impl import schema as v2_schema
    from autoapi.v3.schema import builder as v3_builder

    Base.metadata.clear()
    v2_schema._SchemaCache.clear()
    v3_builder._SchemaCache.clear()

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
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=authn.get_principal)
    authn.register_inject_hook(api)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    client = TestClient(app)
    v2_schema._SchemaCache.clear()
    v3_builder._SchemaCache.clear()
    Base.metadata.clear()
    return client


@pytest.mark.i9n
@pytest.mark.xfail(reason="Owner/Tenant policy integration currently unstable")
def test_tenant_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_tenant(TenantPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post(
        "/item",
        json={"id": str(uuid.uuid4()), "name": "one", "tenant_id": str(tenant_id)},
        headers=headers,
    )
    assert res.status_code == 400

    client = _client_for_tenant(TenantPolicy.CLIENT_SET, user_id, tenant_id)
    supplied = str(uuid.uuid4())
    res = client.post(
        "/item",
        json={"id": str(uuid.uuid4()), "name": "two", "tenant_id": supplied},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["tenant_id"] == supplied
