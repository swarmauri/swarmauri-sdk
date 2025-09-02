from __future__ import annotations
from autoapi.v3 import op_ctx, schema_ctx
from autoapi.v3.bindings import (
    build_handlers,
    build_hooks,
    build_rest,
    build_schemas,
    register_rpc,
)
from autoapi.v3.decorators import collect_decorated_ops
from autoapi.v3.response import response_ctx
from autoapi.v3.runtime import plan as runtime_plan
from pydantic import BaseModel


def build_ping_model():
    @response_ctx(headers={"X-Table": "table"})
    class Widget:
        @schema_ctx(alias="ping", kind="out")
        class PingOut(BaseModel):
            pong: bool

        @op_ctx(alias="ping", target="custom", arity="collection", persist="none")
        @response_ctx(headers={"X-Op": "op"})
        def ping(cls, ctx):
            return {"pong": True}

    specs = list(collect_decorated_ops(Widget))
    build_schemas(Widget, specs)
    build_hooks(Widget, specs)
    build_handlers(Widget, specs)
    runtime_plan.attach_atoms_for_model(Widget, {})
    build_rest(Widget, specs)
    register_rpc(Widget, specs)
    return Widget
