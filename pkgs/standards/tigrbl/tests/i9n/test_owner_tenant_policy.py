from tigrbl.types import App, HTTPException, Request, Security
from typing import Iterable

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
import pytest
import uuid
from sqlalchemy import Column, String

from tigrbl import TigrblApp, Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.mixins.ownable import Ownable, OwnerPolicy
from tigrbl.orm.mixins.tenant_bound import TenantBound, TenantPolicy
from tigrbl.config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from tigrbl.types.authn_abc import AuthNProvider


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
        setattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, principal)
        return principal


def _client_for_owner(
    policy: OwnerPolicy,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    extra_user_ids: Iterable[uuid.UUID] | None = None,
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
        __tigrbl_owner_policy__ = policy

    from tigrbl.engine.shortcuts import mem
    from tigrbl.engine.engine_spec import EngineSpec
    from tigrbl.engine._engine import Engine

    engine = Engine(EngineSpec.from_any(mem(async_=False)))
    db_engine, _ = engine.raw()
    Base.metadata.create_all(bind=db_engine)

    with engine.session() as session:
        session.execute(User.__table__.insert().values(id=user_id, name="owner"))
        for extra in extra_user_ids or []:
            session.execute(User.__table__.insert().values(id=extra, name="extra"))
        session.commit()

    authn = DummyAuth(user_id, tenant_id)
    api = TigrblApp(engine=engine)
    api.set_auth(authn=authn.get_principal)
    api.include_models([User, Item])
    app = App()
    app.include_router(api.router)
    api.initialize()
    return TestClient(app)


@pytest.mark.i9n
def test_owner_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_owner(OwnerPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post(
        "/item",
        json={"name": "one", "owner_id": str(user_id)},
        headers=headers,
    )
    assert res.status_code == 400

    supplied = uuid.uuid4()
    client = _client_for_owner(
        OwnerPolicy.CLIENT_SET, user_id, tenant_id, extra_user_ids=[supplied]
    )
    res = client.post(
        "/item",
        json={"name": "two", "owner_id": str(supplied)},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["owner_id"] == str(supplied)


def _client_for_tenant(
    policy: TenantPolicy,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    extra_tenant_ids: Iterable[uuid.UUID] | None = None,
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
        __tigrbl_tenant_policy__ = policy

    from tigrbl.engine.shortcuts import mem
    from tigrbl.engine.engine_spec import EngineSpec
    from tigrbl.engine._engine import Engine

    engine = Engine(EngineSpec.from_any(mem(async_=False)))
    db_engine, _ = engine.raw()
    Base.metadata.create_all(bind=db_engine)

    with engine.session() as session:
        session.execute(Tenant.__table__.insert().values(id=tenant_id, name="acme"))
        for extra in extra_tenant_ids or []:
            session.execute(Tenant.__table__.insert().values(id=extra, name="extra"))
        session.commit()

    authn = DummyAuth(user_id, tenant_id)
    api = TigrblApp(engine=engine)
    api.set_auth(authn=authn.get_principal)
    api.include_models([Tenant, Item])
    app = App()
    app.include_router(api.router)
    api.initialize()
    return TestClient(app)


@pytest.mark.i9n
def test_tenant_policy_runtime_switch():
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    headers = {"Authorization": "Bearer secret"}

    client = _client_for_tenant(TenantPolicy.STRICT_SERVER, user_id, tenant_id)
    res = client.post(
        "/item",
        json={"name": "one", "tenant_id": str(tenant_id)},
        headers=headers,
    )
    assert res.status_code == 400

    supplied = uuid.uuid4()
    client = _client_for_tenant(
        TenantPolicy.CLIENT_SET, user_id, tenant_id, extra_tenant_ids=[supplied]
    )
    res = client.post(
        "/item",
        json={"name": "two", "tenant_id": str(supplied)},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["tenant_id"] == str(supplied)
