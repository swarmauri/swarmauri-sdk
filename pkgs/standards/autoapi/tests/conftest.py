from typing import Iterator

import pytest_asyncio
from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import BulkCapable, GUIDPk
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest_asyncio.fixture()
async def api_client():
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)
        _nested_path = "/tenants/{tenant_id}"

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(bind=engine)

    def get_db() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db)
    api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Item
