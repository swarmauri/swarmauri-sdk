from autoapi.v3.types import App, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types.authn_abc import AuthNProvider
from autoapi.v3.config import __autoapi_auth_context__

AUTH_CONTEXT_KEY = "auth_context"


class HookedAuth(AuthNProvider):
    async def get_principal(
        self,
        request: Request,
        creds: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> dict:
        if creds.credentials != "secret":
            raise HTTPException(status_code=401)
        principal = {"sub": "user", "tid": "tenant"}
        request.state.principal = principal
        setattr(request.state, __autoapi_auth_context__, principal)
        return principal


def _build_client_with_auth():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"

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
    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.set_auth(authn=auth.get_principal)
    api.include_model(Tenant)
    api.initialize_sync()
    return TestClient(app)


def test_authn_hooks_and_context_injection():
    client = _build_client_with_auth()

    payload = {"id": str(uuid4())}
    res = client.post(
        "/tenant", json=payload, headers={"Authorization": "Bearer secret"}
    )
    assert res.status_code == 201


def test_authn_unauthorized_errors():
    client = _build_client_with_auth()

    assert client.get("/tenant").status_code == 403
    assert (
        client.get("/tenant", headers={"Authorization": "Bearer wrong"}).status_code
        == 401
    )
