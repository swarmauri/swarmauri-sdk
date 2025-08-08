from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Column, String, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import GUIDPk
from autoapi.v2.types import AuthNProvider


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


def test_rpc_endpoint_depends_on_get_principal():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

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
    api = AutoAPI(base=Base, include={Tenant}, get_db=get_db, authn=auth)
    app = FastAPI()
    app.include_router(api.router)

    route = next(r for r in api.router.routes if getattr(r, "path", "") == "/rpc")
    assert any(dep.call == auth.get_principal for dep in route.dependant.dependencies)
