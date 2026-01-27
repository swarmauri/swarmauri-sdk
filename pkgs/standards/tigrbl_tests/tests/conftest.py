import pytest
import pytest_asyncio
from tigrbl import TigrblApp, Base
from tigrbl.types import App
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.column.storage_spec import StorageTransform
from tigrbl.schema import builder as v3_builder
from tigrbl.runtime import kernel as runtime_kernel
from tigrbl.engine.shortcuts import mem
from tigrbl.engine import resolver as _resolver
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, Session
from typing import AsyncIterator, Iterator
import asyncio


def _reset_tigrbl_state() -> None:
    """Reset shared tigrbl state between test modules and tests."""
    Base.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()


@pytest.fixture(scope="session")
def event_loop():
    # pytest-asyncio < 0.21 compatibility pattern; adjust if you use the newer plugin configs
    loop = asyncio.new_event_loop()
    yield loop
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


@pytest.fixture(autouse=True)
def _reset_state():
    """Ensure clean metadata and caches around each test."""
    _reset_tigrbl_state()
    yield
    _reset_tigrbl_state()


def pytest_collect_file(file_path, parent):
    if file_path.suffix == ".py" and file_path.name.startswith("test_"):
        _reset_tigrbl_state()
    return None


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
    """Provide a synchronous in-memory SQLite engine and DB session factory."""
    cfg = mem(async_=False)
    _resolver.set_default(cfg)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()

    def get_db() -> Iterator[Session]:
        with maker() as session:
            yield session

    try:
        yield engine, get_db
    finally:
        engine.dispose()
        _resolver.set_default(None)


@pytest_asyncio.fixture
async def async_db_session():
    """Provide an asynchronous in-memory SQLite engine and DB session factory."""
    cfg = mem()
    _resolver.set_default(cfg)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()

    async def get_db() -> AsyncIterator[AsyncSession]:
        async with maker() as session:
            yield session

    try:
        yield engine, get_db
    finally:
        await engine.dispose()
        _resolver.set_default(None)


@pytest.fixture
def create_test_api():
    """Factory fixture to create Tigrbl instances for testing individual models."""

    def _create_api(model_class):
        """Create Tigrbl instance with a single model for testing."""
        Base.metadata.clear()
        api = TigrblApp(engine=mem(async_=False))
        api.include_model(model_class)
        api.initialize()
        return api

    return _create_api


@pytest_asyncio.fixture
async def create_test_api_async():
    """Factory fixture to create async Tigrbl instances for testing individual models."""

    def _create_api_async(model_class):
        Base.metadata.clear()
        api = TigrblApp(engine=mem())
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
        def __tigrbl_nested_paths__(cls):
            return "/tenant/{tenant_id}/item"

    fastapi_app = App()

    if db_mode == "async":
        api = TigrblApp(engine=mem())
        api.include_models([Tenant, Item])
        await api.initialize()

    else:
        api = TigrblApp(engine=mem(async_=False))
        api.include_models([Tenant, Item])
        api.initialize()

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

        __tigrbl_cols__ = {
            "id": id,
            "name": name,
            "age": age,
            "secret": secret,
        }

    cfg = mem()
    fastapi_app = App()
    api = TigrblApp(engine=cfg)
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    api.attach_diagnostics()
    await api.initialize()
    prov = _resolver.resolve_provider()
    _, session_maker = prov.ensure()
    fastapi_app.include_router(api.router)
    transport = ASGITransport(app=fastapi_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Widget, session_maker
