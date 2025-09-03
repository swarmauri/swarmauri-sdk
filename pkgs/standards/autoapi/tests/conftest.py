import os
import asyncio
import contextlib
import socket
import subprocess
import tempfile
import time
import shutil
import pwd
import pytest
import pytest_asyncio
from autoapi.v3 import AutoApp, Base
from autoapi.v3.types import App
from autoapi.v3.orm.mixins import BulkCapable, GUIDPk
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.column.storage_spec import StorageTransform
from autoapi.v3.schema import builder as v3_builder
from autoapi.v3.runtime import kernel as runtime_kernel
from autoapi.v3.engine.shortcuts import mem, pga, pgs
from autoapi.v3.engine import resolver as _resolver
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, Session
from typing import Any, AsyncIterator, Iterator

os.environ["PATH"] = "/usr/lib/postgresql/16/bin:" + os.environ.get("PATH", "")


def _find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def pg_server() -> dict[str, Any]:
    """Spin up a temporary PostgreSQL server for tests."""
    data_dir = tempfile.mkdtemp()
    uid = pwd.getpwnam("postgres").pw_uid
    gid = pwd.getpwnam("postgres").pw_gid
    os.chown(data_dir, uid, gid)
    port = _find_free_port()
    initdb_cmd = (
        f"/usr/lib/postgresql/16/bin/pg_ctl initdb -D {data_dir} -o '--auth=trust'"
    )
    subprocess.check_call(["su", "postgres", "-c", initdb_cmd])
    start_cmd = f"/usr/lib/postgresql/16/bin/postgres -D {data_dir} -F -p {port}"
    proc = subprocess.Popen(
        ["su", "postgres", "-c", start_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for _ in range(50):
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.terminate()
        proc.wait()
        shutil.rmtree(data_dir)
        raise RuntimeError("PostgreSQL failed to start")
    try:
        yield {"host": "localhost", "port": port, "user": "postgres", "db": "postgres"}
    finally:
        proc.terminate()
        proc.wait()
        shutil.rmtree(data_dir)


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
def pg_db_session(pg_server: dict[str, Any]):
    """Provide a synchronous PostgreSQL engine and DB session factory."""
    cfg = pgs(
        host=pg_server["host"],
        port=pg_server["port"],
        user=pg_server["user"],
        pwd="",
        name=pg_server["db"],
    )
    _resolver.set_default(cfg)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()

    @contextlib.contextmanager
    def get_db() -> Iterator[Session]:
        with maker() as session:
            yield session

    try:
        yield engine, get_db
    finally:
        engine.dispose()
        _resolver.set_default(None)


@pytest_asyncio.fixture
async def async_pg_db_session(pg_server: dict[str, Any]):
    """Provide an asynchronous PostgreSQL engine and DB session factory."""
    cfg = pga(
        host=pg_server["host"],
        port=pg_server["port"],
        user=pg_server["user"],
        pwd="",
        name=pg_server["db"],
    )
    _resolver.set_default(cfg)
    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()

    @contextlib.asynccontextmanager
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
        api = AutoApp(engine=mem())
        api.include_models([Tenant, Item])
        await api.initialize_async()

    else:
        api = AutoApp(engine=mem(async_=False))
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

    cfg = mem()
    fastapi_app = App()
    api = AutoApp(engine=cfg)
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc()
    api.attach_diagnostics()
    await api.initialize_async()
    prov = _resolver.resolve_provider()
    _, session_maker = prov.ensure()
    fastapi_app.include_router(api.router)
    transport = ASGITransport(app=fastapi_app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, api, Widget, session_maker
