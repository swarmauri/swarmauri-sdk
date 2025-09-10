import json

from tigrbl import (
    alias_ctx,
    alias,
    op_ctx,
    schema_ctx,
    SchemaRef,
)
from tigrbl.op import resolve
from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.bindings import build_schemas, build_hooks, build_handlers, build_rest

# REST test client
from tigrbl.types import App, BaseModel
from fastapi.testclient import TestClient


@alias_ctx(read=alias("get", response_schema="Search.out"))
class Widget:
    # --- model-scoped schemas via schema_ctx -------------------------------

    @schema_ctx(alias="Search", kind="in")
    class SearchParams(BaseModel):
        q: str

    @schema_ctx(alias="Search", kind="out")
    class SearchResult(BaseModel):
        id: int
        name: str

    # --- custom ops via op_ctx --------------------------------------------

    @op_ctx(
        alias="search",
        target="custom",
        arity="collection",
        request_schema="Search.in",  # dotted form
        response_schema=SchemaRef("Search", "out"),  # SchemaRef form
    )
    def search(cls, ctx):
        # return id as a string so we can verify serialization/coercion to int
        q = (ctx.get("payload") or {}).get("q")
        return {"id": "7", "name": str(q) if q is not None else None}

    @op_ctx(
        alias="ping",
        target="custom",
        arity="collection",
        response_schema="raw",  # explicit raw → no serialization
    )
    def ping(cls, ctx):
        return json.dumps({"id": "5", "name": "x"})


def _build_all(model):
    """
    Helper: collect specs (canonical + ctx-only) and bind all concerns needed
    for the tests. We only build handlers for ctx-only specs to avoid touching
    canonical CRUD cores during the test.
    """
    canon = resolve(model)  # canonical specs (alias_ctx applied)
    custom = mro_collect_decorated_ops(model)  # ctx-only specs
    specs = canon + custom

    # Schemas first (seeds schema_ctx, then defaults, then overrides)
    build_schemas(model, specs)
    # Hooks (none in this test, but normalize structure)
    build_hooks(model, specs)
    # Handlers: only for ctx-only specs we will actually invoke
    build_handlers(model, custom)
    # REST router for all specs (we'll only call custom endpoints)
    build_rest(model, specs)

    return specs


def test_schema_ctx_seed_and_alias_ctx_override():
    _build_all(Widget)

    # schema_ctx seeded schemas exist under model.schemas.<Alias>.in_/out
    assert hasattr(Widget, "schemas")
    assert hasattr(Widget.schemas, "Search")
    assert Widget.schemas.Search.in_.__name__ == "SearchParams"
    assert Widget.schemas.Search.out.__name__ == "SearchResult"

    # alias_ctx renamed canonical read → get, and applied response override
    assert hasattr(Widget.schemas, "get")
    assert Widget.schemas.get.out is Widget.SearchResult


def test_rest_serialization_with_and_without_out_schema():
    _build_all(Widget)

    app = App()
    # Router was attached by build_rest
    app.include_router(Widget.rest.router)
    client = TestClient(app)

    # custom op "search" (collection + custom path): /widget/search
    # request_schema is applied; response_schema enforces typing (id coerced to int)
    r1 = client.post("/widget/search", json={"q": "abc"})
    assert r1.status_code == 200
    assert r1.json() == {"id": 7, "name": "abc"}  # id coerced by out schema

    # confirm request schema coercion: q=int → str
    r2 = client.post("/widget/search", json={"q": 123})
    # Invalid type for ``q`` now triggers a 422 validation error
    assert r2.status_code == 422

    # custom op "ping" uses response_schema="raw" → no serialization/coercion
    r3 = client.post("/widget/ping", json={})
    assert r3.status_code == 200
    assert r3.json() == {"id": "5", "name": "x"}  # stays raw (no coercion)
