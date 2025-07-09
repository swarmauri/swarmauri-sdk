from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import BulkCapable, GUIDPk
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


def pytest_addoption(parser):
    """Add command line options for database mode."""
    group = parser.getgroup("database")
    group.addoption(
        "--db-mode",
        choices=["sync", "async"],
        help="Database mode to test (sync or async). If not specified, tests both modes.",
    )


def pytest_generate_tests(metafunc):
    """Generate test parameters for db modes."""
    if "db_mode" in metafunc.fixturenames:
        db_mode_option = metafunc.config.getoption("--db-mode")
        if db_mode_option:
            # Run only the specified mode
            metafunc.parametrize("db_mode", [db_mode_option])
        else:
            # Run both modes by default
            metafunc.parametrize("db_mode", ["sync", "async"])


@pytest_asyncio.fixture()
async def api_client(db_mode):
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)
        _nested_path = "/tenants/{tenant_id}"

    if db_mode == "async":
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

        AsyncSessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        async def get_async_db() -> AsyncIterator[AsyncSession]:
            async with AsyncSessionLocal() as session:
                yield session

        api = AutoAPI(base=Base, include={Tenant, Item}, get_async_db=get_async_db)
        await api.initialize_async()

    else:
        engine = create_engine(
            "sqlite:///:memory:", connect_args={"check_same_thread": False}
        )

        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

        def get_sync_db() -> Iterator[Session]:
            with SessionLocal() as session:
                yield session

        api = AutoAPI(base=Base, include={Tenant, Item}, get_db=get_sync_db)
        api.initialize_sync()

    app = FastAPI()
    app.include_router(api.router)
    transport = ASGITransport(app=app)

    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Item