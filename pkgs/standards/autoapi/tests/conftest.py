from typing import Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from autoapi.v2 import AutoAPI, Base
from autoapi.v2.engines import blocking_postgres_engine, blocking_sqlite_engine
from autoapi.v2.mixins import BulkCapable, GUIDPk


@pytest.fixture(params=["sqlite", "postgres"])
def session_factory(request):
    if request.param == "postgres":
        try:
            engine, SessionLocal = blocking_postgres_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            pytest.skip("PostgreSQL not available")
    else:
        engine, SessionLocal = blocking_sqlite_engine()
    Base.metadata.clear()
    request.addfinalizer(engine.dispose)
    return SessionLocal


@pytest_asyncio.fixture()
async def api_client(session_factory):
    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)
        _nested_path = "/tenants/{tenant_id}"

    def get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_db)
    api.initialize_sync()
    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, api, Item
