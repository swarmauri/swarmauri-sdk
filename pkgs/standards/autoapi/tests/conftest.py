from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from autoapi.v3 import AutoApp, Base
from autoapi.v3.types import App
from autoapi.v3.orm.mixins import BulkCapable, GUIDPk
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.column.storage_spec import StorageTransform
from autoapi.v3.schema import builder as v3_builder
from autoapi.v3.runtime import kernel as runtime_kernel
from autoapi.v3.engine.shortcuts import mem
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, Session, sessionmaker
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    # pytest-asyncio < 0.21 compatibility pattern; adjust if you use the newer plugin configs
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def _reset_state():
    """Ensure clean metadata and caches around each test."""
    Base.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()
    yield
    Base.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()


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
def create_test_api():
    """Factory fixture to create AutoAPI instances for testing individual models."""

    def _create_api(model_class):
        """Create AutoAPI instance with a single model for testing."""
        Base.metadata.clear()
        api = AutoApp(engine=mem(async_=False))
        api.include_model(model_class)
        api.initialize_sync()
        return api

    return _create_api


@pytest_asyncio.fixture
async def create_test_api_async():
    """Factory fixture to create async AutoAPI instances for testing individual models."""

    def _create_api_async(model_class):
        Base.metadata.clear()
        api = AutoApp(engine=mem())
        api.include_model(model_class)
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
        name = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                mutable_verbs=("create", "update", "replace"),
                filter_ops=("eq",),
            ),
        )

    class Item(Base, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __autoapi_nested_paths__(cls):
            return "/tenant/{tenant_id}/item"

    fastapi_app = App()

    if db_mode == "async":
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

        AsyncSessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        async def get_db() -> AsyncIterator[AsyncSession]:
            async with AsyncSessionLocal() as session:
                yield session

        api = AutoApp(get_db=get_db)
        api.include_models([Tenant, Item])
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

        api = AutoApp(get_db=get_sync_db)
        api.include_models([Tenant, Item])
        api.initialize_sync()

    api.mount_jsonrpc()
    fastapi_app.include_router(api.router)
    transport = ASGITransport(app=fastapi_app)

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


@pytest_asyncio.fixture()
async def api_client_v3():
    Base.metadata.clear()

    class Widget(Base):
        __tablename__ = "widgets"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False, index=True),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update"),
                out_verbs=("read", "list"),
            ),
        )
        age: Mapped[int] = acol(
            storage=S(type_=Integer, nullable=False, default=5),
            io=IO(
                in_verbs=("create", "update"),
                out_verbs=("read", "list"),
            ),
        )
        secret: Mapped[str] = acol(
            storage=S(
                type_=String,
                nullable=False,
                transform=StorageTransform(to_stored=lambda v, ctx: v.upper()),
            ),
            field=F(required_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

        __autoapi_cols__ = {
            "id": id,
            "name": name,
            "age": age,
            "secret": secret,
        }

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session

    fastapi_app = App()
    api = AutoApp(get_db=get_db)
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    api.attach_diagnostics()
    fastapi_app.include_router(api.router)
    transport = ASGITransport(app=fastapi_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Widget, AsyncSessionLocal
