import asyncio
from unittest.mock import AsyncMock, patch

from pydantic import BaseModel

from tigrbl import op_ctx
from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.schema.decorators import schema_ctx
from tigrbl.op import resolve
from tigrbl.bindings import build_schemas, build_hooks, build_handlers, build_rest


def _build_all(model):
    canon = resolve(model)
    custom = mro_collect_decorated_ops(model)
    specs = canon + custom
    build_schemas(model, specs)
    build_hooks(model, specs)
    build_handlers(model, custom)
    build_rest(model, specs)
    return custom


def test_op_ctx_alias_attribute():
    class Widget:
        @op_ctx(alias="foo")
        def op(cls, ctx):
            return None

    specs = mro_collect_decorated_ops(Widget)
    assert specs[0].alias == "foo"


def test_op_ctx_default_target_custom_runs_logic():
    class Gadget:
        @op_ctx()
        def ping(cls, ctx):
            return {"ok": True}

    specs = _build_all(Gadget)
    assert Gadget.ping({}) == {"ok": True}
    assert specs[0].target == "custom"


def test_op_ctx_canonical_target_uses_core():
    class Gadget:
        @op_ctx(target="read")
        def get(cls, ctx):
            ctx["called"] = True
            return {"id": 1}

    _build_all(Gadget)

    ctx = {"path_params": {"id": 1}}
    with patch("tigrbl.core.read", AsyncMock(return_value={"id": 2})) as core_read:
        rv = asyncio.run(Gadget.handlers.get.handler(ctx))
    assert rv == {"id": 2}
    assert "called" not in ctx
    core_read.assert_awaited_once()


def test_op_ctx_arity_collection_routing():
    class Gadget:
        @op_ctx(alias="stats", arity="collection")
        def stats(cls, ctx):
            return {"ok": True}

    specs = _build_all(Gadget)
    routes = {r.path: r.methods for r in Gadget.rest.router.routes}
    assert "/gadget/stats" in routes
    assert "POST" in routes["/gadget/stats"]
    assert specs[0].arity == "collection"


def test_op_ctx_rest_false_hides_route():
    class Gadget:
        @op_ctx(alias="hidden", rest=False)
        def hidden(cls, ctx):
            return {"ok": True}

    specs = _build_all(Gadget)
    routes = {r.path for r in Gadget.rest.router.routes}
    assert "/gadget/hidden" not in routes
    assert specs[0].expose_routes is False


def test_op_ctx_request_schema_coercion():
    class Gadget:
        @schema_ctx(alias="Payload", kind="in")
        class Payload(BaseModel):
            x: int

        @op_ctx(alias="check", request_schema="Payload.in")
        def check(cls, ctx):
            v = ctx["payload"]["x"]
            return {"x": v, "type": type(v).__name__}

    _build_all(Gadget)
    model = Gadget.schemas.check.in_
    parsed = model(x="5")
    assert parsed.x == 5
    assert isinstance(parsed.x, int)


def test_op_ctx_response_schema_coercion():
    class Gadget:
        @schema_ctx(alias="Result", kind="out")
        class Result(BaseModel):
            x: int

        @op_ctx(alias="check", response_schema="Result.out")
        def check(cls, ctx):
            return {"x": "5"}

    _build_all(Gadget)
    model = Gadget.schemas.check.out
    parsed = model(x="5")
    assert parsed.x == 5


def test_op_ctx_direct_model_schemas():
    class Gadget:
        class Payload(BaseModel):
            x: int

        class Result(BaseModel):
            x: int

        @op_ctx(alias="check", request_schema=Payload, response_schema=Result)
        def check(cls, ctx):
            return {"x": ctx["payload"]["x"]}

    _build_all(Gadget)
    in_model = Gadget.schemas.check.in_
    out_model = Gadget.schemas.check.out
    assert in_model(x="5").x == 5
    assert out_model(x="5").x == 5


def test_op_ctx_persist_attribute():
    class Gadget:
        @op_ctx(persist="skip")
        def op(cls, ctx):
            return None

    specs = mro_collect_decorated_ops(Gadget)
    assert specs[0].persist == "skip"
