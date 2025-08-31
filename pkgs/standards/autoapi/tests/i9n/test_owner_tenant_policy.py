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
from autoapi.v3.config.constants import AUTOAPI_AUTH_CONTEXT_ATTR


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
        setattr(request.state, AUTOAPI_AUTH_CONTEXT_ATTR, principal)
        return principal


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
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=authn.get_principal)
    api.include_models([User, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


@pytest.mark.i9n
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
    api = AutoAPI(get_db=get_db)
    api.set_auth(authn=authn.get_principal)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


@pytest.mark.i9n
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
