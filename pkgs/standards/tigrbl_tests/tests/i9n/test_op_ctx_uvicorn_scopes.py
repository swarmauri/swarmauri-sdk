from itertools import product

import pytest

from tigrbl import TigrblApp, TigrblRouter, op_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.types import BaseModel, Column, String


class TokenInventorySchema(BaseModel):
    access_tokens: int
    refresh_tokens: int


PERSIST_VARIANTS = (
    "default",
    "write",
    "append",
    "prepend",
    "override",
    "skip",
    "none",
    "read",
)
ARITY_VARIANTS = ("collection", "member")
RESPONSE_SCHEMA_VARIANTS = (None, TokenInventorySchema)
SCOPE_VARIANTS = ("table", "router", "app")


@pytest.fixture(autouse=True)
def _disable_docs_mounts(monkeypatch):
    """Keep this matrix focused on op_ctx behavior, not optional docs deps."""
    import tigrbl_concrete._concrete.tigrbl_app as tigrbl_app_module

    monkeypatch.setattr(TigrblApp, "mount_openapi", lambda self, **_: None)
    monkeypatch.setattr(TigrblApp, "mount_openrpc", lambda self, **_: None)
    monkeypatch.setattr(TigrblApp, "mount_lens", lambda self, **_: None)
    monkeypatch.setattr(TigrblApp, "attach_diagnostics", lambda self, **_: None)
    monkeypatch.setattr(tigrbl_app_module, "_mount_swagger", lambda *_, **__: None)


def _op_payload() -> dict[str, int]:
    return {"access_tokens": 3, "refresh_tokens": 1}


def _member_path(resource: str, alias: str) -> str:
    return f"/{resource}/{{item_id}}/{alias}"


def _collection_path(resource: str, alias: str) -> str:
    return f"/{resource}/{alias}"


def _build_table_app(
    arity: str, response_schema, persist: str
) -> tuple[TigrblApp, str]:
    TableBase.metadata.clear()
    schema_tag = "with_schema" if response_schema is not None else "no_schema"

    class InventoryTable(TableBase, GUIDPk):
        __tablename__ = f"inventory_table_op_ctx_uvicorn_{arity}_{persist}_{schema_tag}"
        __resource__ = "inventory"
        name = Column(String)

        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity=arity,
            response_schema=response_schema,
            persist=persist,
        )
        def token_inventory(cls, ctx):
            return _op_payload()

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(InventoryTable, prefix="")
    app.initialize()
    path = (
        _collection_path("inventory", "token_inventory")
        if arity == "collection"
        else _member_path("inventory", "token_inventory")
    )
    return app, path


async def _build_router_app(
    arity: str, response_schema, persist: str
) -> tuple[TigrblApp, str]:
    TableBase.metadata.clear()
    schema_tag = "with_schema" if response_schema is not None else "no_schema"

    class InventoryTable(TableBase, GUIDPk):
        __tablename__ = (
            f"inventory_router_op_ctx_uvicorn_{arity}_{persist}_{schema_tag}"
        )
        __resource__ = "inventory"
        name = Column(String)

        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity=arity,
            response_schema=response_schema,
            persist=persist,
        )
        def token_inventory(cls, ctx):
            return _op_payload()

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(InventoryTable, prefix="")
    await router.initialize()

    app = TigrblApp(engine=mem(async_=False))
    app.include_router(router)
    app.initialize()
    path = (
        _collection_path("inventory", "token_inventory")
        if arity == "collection"
        else _member_path("inventory", "token_inventory")
    )
    return app, path


def _build_app_local_op(
    arity: str, response_schema, persist: str
) -> tuple[TigrblApp, str]:
    TableBase.metadata.clear()

    class InventoryApp(TigrblApp):
        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity=arity,
            response_schema=response_schema,
            persist=persist,
        )
        def token_inventory(cls, ctx):
            return _op_payload()

    app = InventoryApp(engine=mem(async_=False))
    app.initialize()
    path = (
        _collection_path("inventoryapp", "token_inventory")
        if arity == "collection"
        else _member_path("inventoryapp", "token_inventory")
    )
    return app, path


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scope,arity,response_schema,persist",
    list(
        product(
            SCOPE_VARIANTS, ARITY_VARIANTS, RESPONSE_SCHEMA_VARIANTS, PERSIST_VARIANTS
        )
    ),
    ids=lambda v: getattr(v, "__name__", str(v)),
)
async def test_uvicorn_client_call_with_op_ctx_parameter_combinations(
    scope: str, arity: str, response_schema, persist: str
) -> None:
    if scope == "table":
        app, path = _build_table_app(arity, response_schema, persist)
    elif scope == "router":
        app, path = await _build_router_app(arity, response_schema, persist)
    else:
        app, path = _build_app_local_op(arity, response_schema, persist)

    matching_routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == path
        and "POST" in (getattr(route, "methods", set()) or set())
    ]

    assert matching_routes, (
        f"Expected a POST route for {scope=} {arity=} {persist=} at {path!r}, "
        "but none was registered."
    )
