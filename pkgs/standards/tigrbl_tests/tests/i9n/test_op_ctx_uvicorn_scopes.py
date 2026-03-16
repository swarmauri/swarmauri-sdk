import uuid
from itertools import product
from inspect import isawaitable

import httpx
import pytest

from tigrbl import TigrblApp, TigrblRouter, op_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.types import BaseModel, Column, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


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


def _op_payload() -> dict[str, int]:
    return {"access_tokens": 3, "refresh_tokens": 1}


def _member_path(resource: str, alias: str, item_id: str | None = None) -> str:
    resolved_item_id = item_id or str(uuid.uuid4())
    return f"/{resource}/{resolved_item_id}/{alias}"


def _collection_path(resource: str, alias: str) -> str:
    return f"/{resource}/{alias}"


def _table_name(prefix: str, arity: str, persist: str, schema_tag: str) -> str:
    """Build a unique table name to avoid collisions across parallel test workers."""
    return f"{prefix}_{arity}_{persist}_{schema_tag}_{uuid.uuid4().hex[:8]}"


def _build_table_app(
    arity: str, response_schema, persist: str
) -> tuple[TigrblApp, str]:
    TableBase.metadata.clear()
    schema_tag = "with_schema" if response_schema is not None else "no_schema"

    class InventoryTable(TableBase, GUIDPk):
        __tablename__ = _table_name(
            "inventory_table_op_ctx_uvicorn", arity, persist, schema_tag
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

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(InventoryTable, prefix="")
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
        __tablename__ = _table_name(
            "inventory_router_op_ctx_uvicorn", arity, persist, schema_tag
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

    app.attach_diagnostics()
    initialize_result = app.initialize()
    if isawaitable(initialize_result):
        await initialize_result

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}{path}", json={})

        assert response.status_code in {200, 204}
        if response.status_code == 200:
            assert response.content
            assert response.json() == _op_payload()
        else:
            assert response.status_code == 204
            assert not response.content
    finally:
        await stop_uvicorn_server(server, task)
