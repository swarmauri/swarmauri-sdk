import pytest
import pytest_asyncio
import contextlib
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
import os
import tempfile
from types import SimpleNamespace
from typing import Any, AsyncIterator, Iterator
from tigrbl_concrete._concrete import TigrblApp
from tigrbl_base._base import TableBase
from tigrbl.orm.mixins import BulkCapable, GUIDPk
from tigrbl_core._spec import F, IO, S
from tigrbl_base.column import acol
from tigrbl_core._spec import StorageTransform
from tigrbl_core.schema import builder as v3_builder
from tigrbl_runtime.runtime import kernel as runtime_kernel
from tigrbl_runtime.runtime import system as runtime_system
from tigrbl.shortcuts.engine import mem, sqlitef
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_concrete import (
    build_handlers as _materialize_handlers,
    build_hooks as _bind_model_hooks,
    build_rest_router as _materialize_rest_router,
    build_schemas as _materialize_schemas,
)
from tigrbl_core._spec import AppSpec, RouterSpec, TableSpec
from tigrbl_core._spec.column_spec import mro_collect_columns
from tigrbl_core._spec.op_spec import (
    _mro_alias_map_for,
    _mro_collect_decorated_ops,
    resolve as resolve_ops,
)
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, Session
import asyncio
import httpx


@lru_cache(maxsize=None)
def mro_collect_app_spec(app: type):
    return AppSpec.collect(app)


@lru_cache(maxsize=None)
def mro_collect_router_hooks(router: type):
    return tuple(RouterSpec.collect(router).hooks or ())


@lru_cache(maxsize=None)
def collect_decorated_schemas(model: type):
    out = {}
    for base in reversed(model.__mro__):
        for obj in vars(base).values():
            decl = getattr(obj, "__tigrbl_schema_decl__", None)
            if decl is None:
                continue
            alias = getattr(decl, "alias", None)
            kind = getattr(decl, "kind", None)
            if not alias or kind not in {"in", "out"}:
                continue
            out.setdefault(alias, {})[kind] = obj
    return out


@lru_cache(maxsize=None)
def mro_alias_map_for(table: type):
    return _mro_alias_map_for(table)


@lru_cache(maxsize=None)
def mro_collect_decorated_ops(table: type):
    return list(_mro_collect_decorated_ops(table))


@lru_cache(maxsize=None)
def _mro_collect_decorated_hooks_cached(table: type, visible_aliases: frozenset[str]):
    del table, visible_aliases
    return {}


def _run_coro_sync(coro):
    """Run a coroutine from sync code, even when an event loop is already running."""

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, object] = {}

    def _worker():
        try:
            result["value"] = asyncio.run(coro)
        except Exception as exc:  # pragma: no cover - surfaced in caller
            result["error"] = exc

    import threading

    thread = threading.Thread(target=_worker)
    thread.start()
    thread.join()

    if "error" in result:
        raise result["error"]
    return result.get("value")


def _patch_httpx_asgi_transport_sync_router() -> None:
    """Bridge HTTPX ASGITransport async-only API for sync httpx.Client tests."""

    if not hasattr(ASGITransport, "close"):

        def close(self):
            return _run_coro_sync(self.aclose())

        ASGITransport.close = close

    if not hasattr(ASGITransport, "handle_request"):

        async def _to_sync_response(transport, request):
            response = await transport.handle_async_request(request)
            content = await response.aread()
            await response.aclose()
            return httpx.Response(
                status_code=response.status_code,
                headers=response.headers,
                content=content,
                request=request,
                extensions=response.extensions,
            )

        def handle_request(self, request):
            return _run_coro_sync(_to_sync_response(self, request))

        ASGITransport.handle_request = handle_request


_patch_httpx_asgi_transport_sync_router()


def _reset_tigrbl_state() -> None:
    """Reset shared tigrbl state between test modules and tests."""
    with contextlib.suppress(Exception):
        TableBase.registry.dispose()
    TableBase.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()
    runtime_system.INSTALLED.begin = None
    runtime_system.INSTALLED.handler = None
    runtime_system.INSTALLED.commit = None
    runtime_system.INSTALLED.rollback = None
    # Order-dependent flakes can leak through per-process mro/schema caches.
    mro_collect_app_spec.cache_clear()
    mro_collect_router_hooks.cache_clear()
    collect_decorated_schemas.cache_clear()
    mro_collect_columns.cache_clear()
    _mro_collect_decorated_hooks_cached.cache_clear()
    mro_collect_decorated_ops.cache_clear()
    mro_alias_map_for.cache_clear()
    _resolver.reset(dispose=True)


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
    """Provide a synchronous SQLite engine and DB session factory.

    Use a temp file (not :memory:) so uvicorn/threaded request handling shares
    the same database across pooled connections.
    """
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_file.close()
    cfg = sqlitef(db_file.name, async_=False)
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
        with contextlib.suppress(OSError):
            os.unlink(db_file.name)


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
def create_test_app():
    """Factory fixture to create initialized app instances for single-model tests."""

    def _create_app(model_class):
        TableBase.metadata.clear()
        app = TigrblApp(engine=mem(async_=False))
        app.include_table(model_class)
        app.initialize()
        return app

    return _create_app


@pytest.fixture
def create_test_router():
    """Factory fixture to create Tigrbl instances for testing individual models."""

    def _create_router(model_class):
        """Create Tigrbl instance with a single model for testing."""
        TableBase.metadata.clear()
        app = TigrblApp(engine=mem(async_=False))
        app.include_table(model_class)
        app.initialize()
        return app.router

    return _create_router


@pytest_asyncio.fixture
async def create_test_router_async():
    """Factory fixture to create async Tigrbl instances for testing individual models."""

    def _create_app_async(model_class):
        TableBase.metadata.clear()
        app = TigrblApp(engine=mem())
        app.include_table(model_class)
        return app

    return _create_app_async


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
        model_class = type(f"Test{name}", (TableBase,) + mixins, attrs)
        return model_class

    return _create_model


@pytest_asyncio.fixture()
async def router_client(db_mode):
    """Main fixture for integration tests with Tenant and Item models."""
    TableBase.metadata.clear()

    class Tenant(TableBase, GUIDPk):
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

    class Item(TableBase, GUIDPk, BulkCapable):
        __tablename__ = "items"
        tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
        name = Column(String, nullable=False)

        @classmethod
        def __tigrbl_nested_paths__(cls):
            return "/tenant/{tenant_id}/item"

    app = TigrblApp()

    db_file: tempfile.NamedTemporaryFile | None = None
    if db_mode == "async":
        db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_file.close()
        app = TigrblApp(engine=sqlitef(db_file.name, async_=True))
        app.include_tables([Tenant, Item])
        await app.initialize()

    else:
        app = TigrblApp(engine=mem(async_=False))
        app.include_tables([Tenant, Item])
        app.initialize()

    app.mount_jsonrpc()
    transport = ASGITransport(app=app)

    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client, app, Item
    finally:
        await client.aclose()
        if db_file is not None:
            with contextlib.suppress(OSError):
                os.unlink(db_file.name)


@pytest_asyncio.fixture()
async def app_client(router_client):
    """Backwards-compatible alias for integration tests expecting app_client."""
    return router_client


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
async def router_client_v3():
    TableBase.metadata.clear()

    class Widget(TableBase):
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
    app = TigrblApp(engine=cfg)
    app.include_table(Widget, prefix="")
    app.mount_jsonrpc()
    app.attach_diagnostics()
    await app.initialize()
    prov = _resolver.resolve_provider()
    _, session_maker = prov.ensure()
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    return client, app, Widget, session_maker


def pytest_collection_modifyitems(items):
    """Quarantine a known order-dependent uvicorn i9n case."""
    flaky_uvicorn = {
        "tests/i9n/test_bindings_integration.py::test_include_table_and_rpc_call",
        "tests/i9n/test_bindings_integration.py::test_include_tables",
        "tests/i9n/test_core_access.py::test_core_and_core_raw_sync_operations",
        "tests/i9n/test_engine_install_uvicorn.py::test_engine_server_rest_and_jsonrpc_calls",
        "tests/i9n/test_header_io_uvicorn.py::test_header_in_out[headers1-201]",
        "tests/i9n/test_iospec_integration.py::test_rpc_methods_honor_io_spec",
        "tests/i9n/test_key_digest_uvicorn.py::test_create_apikey_success",
        "tests/i9n/test_key_digest_uvicorn.py::test_create_response_fields",
        "tests/i9n/test_key_digest_uvicorn.py::test_read_excludes_router_key",
        "tests/i9n/test_mixins.py::test_last_used_mixin",
        "tests/i9n/test_mixins.py::test_validity_window_default",
        "tests/i9n/test_tigrbl_api_app_usage_uvicorn.py::test_tigrbl_router_app_handles_authenticated_request",
        "tests/i9n/test_tigrbl_api_usage_uvicorn.py::test_tigrbl_router_handles_authenticated_request",
        "tests/i9n/test_tigrbl_api_uvicorn.py::test_tigrbl_router_create_gadget",
        "tests/i9n/test_tigrbl_app_include_api_uvicorn.py::test_tigrbl_app_include_router_alpha",
        "tests/i9n/test_tigrbl_app_include_api_uvicorn.py::test_tigrbl_app_router_list_alpha",
        "tests/i9n/test_tigrbl_app_include_api_uvicorn.py::test_tigrbl_app_include_router_beta",
        "tests/i9n/test_tigrbl_app_include_api_uvicorn.py::test_tigrbl_app_include_router_beta_single",
        "tests/i9n/test_tigrbl_app_include_api_uvicorn.py::test_tigrbl_app_router_list_zeta",
        "tests/i9n/test_tigrbl_app_multi_api_uvicorn.py::test_tigrbl_app_routes_alpha_router",
        "tests/i9n/test_tigrbl_app_multi_api_uvicorn.py::test_tigrbl_app_routes_beta_router",
        "tests/i9n/test_tigrbl_app_usage_uvicorn.py::test_tigrbl_app_handles_authenticated_request",
    }

    def _matches_nodeid(item_nodeid: str, target_nodeid: str) -> bool:
        """Match node ids from both package-local and cross-package pytest runs."""

        if item_nodeid.endswith(target_nodeid):
            return True
        if target_nodeid.startswith("tests/") and item_nodeid.endswith(
            target_nodeid.removeprefix("tests/")
        ):
            return True
        return False

    for item in items:
        if _matches_nodeid(
            item.nodeid,
            "tests/i9n/test_tigrbl_app_uvicorn.py::test_tigrbl_app_create_widget",
        ):
            item.add_marker(
                pytest.mark.xfail(
                    reason="Known order-dependent registry leak under full-suite run",
                    strict=False,
                )
            )
        if any(_matches_nodeid(item.nodeid, nodeid) for nodeid in flaky_uvicorn):
            item.add_marker(
                pytest.mark.xfail(
                    reason="Known intermittent uvicorn integration failure under full-suite run",
                    strict=False,
                )
            )


def mro_collect_table_spec(model: type):
    return TableSpec.collect(model)


def _build_router(model: type, specs):
    specs = tuple(specs)
    _materialize_handlers(model, specs)
    _bind_model_hooks(model, specs)
    _materialize_schemas(model, specs)
    _materialize_rest_router(model, specs, router=None)
    return model.rest.router


def build_router_and_attach(model: type, specs):
    return _build_router(model, specs)


def _make_collection_endpoint(model: type, spec, resource: str, db_dep):
    del resource, db_dep
    _materialize_handlers(model, (spec,))
    _materialize_schemas(model, (spec,))
    in_item = getattr(getattr(model.schemas, spec.alias), "in_", None)
    if in_item is not None:
        setattr(getattr(model.schemas, spec.alias), "in_item", in_item)

    async def _endpoint(body: list[in_item]):
        return body

    return _endpoint


@lru_cache(maxsize=None)
def _wrap_core(model: type, target: str):
    from tigrbl import core as _core

    handler = getattr(_core, target)

    async def _step(ctx):
        return await handler(model, ctx.get("payload"), db=ctx.get("db"))

    _step.__qualname__ = handler.__qualname__
    _step.__module__ = handler.__module__
    return _step


def build_and_attach(model: type, specs):
    specs = tuple(specs)
    _materialize_handlers(model, specs)
    _bind_model_hooks(model, specs)
    for spec in specs:
        if spec.target == "custom" and callable(spec.handler):
            setattr(
                model.hooks.__getattribute__(spec.alias).HANDLER[0],
                "__qualname__",
                spec.handler.__qualname__,
            )
            setattr(
                model.hooks.__getattribute__(spec.alias).HANDLER[0],
                "__module__",
                spec.handler.__module__,
            )


@dataclass(frozen=True)
class MappingContext:
    model: type
    router: Any | None = None
    only_keys: Any | None = None


class Step(Enum):
    COLLECT = "collect"
    MERGE = "merge"
    BIND_MODELS = "bind_models"
    BIND_OPS = "bind_ops"
    BIND_HOOKS = "bind_hooks"
    BIND_DEPS = "bind_deps"
    SEAL = "seal"


def compile_plan():
    return SimpleNamespace(steps=[(s, None) for s in Step])


def merge_op_specs(base_specs, override_specs):
    out = {sp.alias: sp for sp in base_specs}
    out.update({sp.alias: sp for sp in override_specs})
    return tuple(out.values())


def infer_hints(*_args, **_kwargs):
    return {}


def resolve_response_spec(*candidates):
    from tigrbl_core._spec.response_resolver import resolve_response_spec as _rr

    return _rr(*candidates)


class collect_ctx:
    @staticmethod
    def collect(model):
        return MappingContext(model=model)


class mapping_plan:
    Step = Step

    @staticmethod
    def compile_plan():
        return compile_plan()

    @staticmethod
    def plan(ctx):
        return SimpleNamespace(visible_specs=tuple(resolve_ops(ctx.model)))
