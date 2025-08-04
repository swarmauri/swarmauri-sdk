from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import BulkCapable, GUIDPk
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, String, create_engine
from sqlalchemy.pool import StaticPool
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


@pytest.fixture
def sync_db_session():
    """Create a sync database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def get_sync_db() -> Iterator[Session]:
        with SessionLocal() as session:
            yield session

    return engine, get_sync_db


@pytest_asyncio.fixture
async def async_db_session():
    """Create an async database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_async_db() -> AsyncIterator[AsyncSession]:
        async with AsyncSessionLocal() as session:
            yield session

    return engine, get_async_db


@pytest.fixture
def create_test_api(sync_db_session):
    """Factory fixture to create AutoAPI instances for testing individual models."""
    engine, get_sync_db = sync_db_session

    def _create_api(model_class, base=None):
        """Create AutoAPI instance with a single model for testing."""
        if base is None:
            base = Base

        # Clear metadata to avoid conflicts
        base.metadata.clear()

        api = AutoAPI(base=base, include={model_class}, get_db=get_sync_db)
        api.initialize_sync()
        return api

    return _create_api


@pytest_asyncio.fixture
async def create_test_api_async(async_db_session):
    """Factory fixture to create async AutoAPI instances for testing individual models."""
    engine, get_async_db = async_db_session

    def _create_api_async(model_class, base=None):
        """Create async AutoAPI instance with a single model for testing."""
        if base is None:
            base = Base

        # Clear metadata to avoid conflicts
        base.metadata.clear()

        api = AutoAPI(base=base, include={model_class}, get_async_db=get_async_db)
        return api

    return _create_api_async


@pytest.fixture
def test_models():
    """Factory fixture to create test model classes."""

    def _create_model(name, mixins=None, extra_fields=None):
        """Create a test model class with specified mixins and fields."""
        if mixins is None:
            mixins = (GUIDPk,)

        attrs = {
            "__tablename__": f"test_{name.lower()}",
            "name": Column(String, nullable=False),
        }

        if extra_fields:
            attrs.update(extra_fields)

        # Create the model class dynamically
        model_class = type(f"Test{name}", (Base,) + mixins, attrs)
        return model_class

    return _create_model


@pytest_asyncio.fixture()
async def api_client(db_mode):
    """Main fixture for integration tests with Tenant and Item models."""
    Base.metadata.clear()

    class Tenant(Base, GUIDPk):
        __tablename__ = "tenants"
        name = Column(String, nullable=False)

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_nested_paths__(cls):
            return "/tenants/{tenant_id}"

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
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
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


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {"name": "test-tenant"}


@pytest.fixture
def sample_item_data():
    """Sample item data for testing (requires tenant_id)."""

    def _create_item_data(tenant_id):
        return {"tenant_id": tenant_id, "name": "test-item"}

    return _create_item_data
