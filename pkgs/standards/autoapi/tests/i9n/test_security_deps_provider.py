from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import GUIDPk


def _build_client():
    Base.metadata.clear()

    class Item(Base, GUIDPk):
        __tablename__ = "items"
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_security_deps__(cls):
            def verify(x_token: str = Header(None)):
                if x_token != "secret":
                    raise HTTPException(status_code=401)

            return [Depends(verify)]

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_db():
        with SessionLocal() as session:
            yield session

    api = AutoAPI(base=Base, include={Item}, get_db=get_db)
    app = FastAPI()
    app.include_router(api.router)
    api.initialize_sync()
    return TestClient(app)


def test_security_deps_enforced():
    client = _build_client()
    payload = {"name": "thing"}
    assert client.post("/item", json=payload).status_code == 401
    res = client.post("/item", json=payload, headers={"x-token": "secret"})
    assert res.status_code == 201
    iid = res.json()["id"]
    assert client.get(f"/item/{iid}").status_code == 401
    assert client.get(f"/item/{iid}", headers={"x-token": "secret"}).status_code == 200
