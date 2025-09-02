from __future__ import annotations
from autoapi.v3 import alias_ctx, op_ctx, schema_ctx
from autoapi.v3.bindings import (
    build_handlers,
    build_hooks,
    build_rest,
    build_schemas,
    register_rpc,
)
from autoapi.v3.decorators import collect_decorated_ops
from autoapi.v3.response import response_ctx, render_template
from autoapi.v3.response.shortcuts import (
    as_file,
    as_html,
    as_json,
    as_redirect,
    as_stream,
    as_text,
)
from autoapi.v3.runtime import plan as runtime_plan
from pydantic import BaseModel
from typing import get_args
from autoapi.v3.response.types import ResponseKind


RESPONSE_KINDS = get_args(ResponseKind)


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


def build_model_for_response(kind: str, tmp_path) -> tuple[type, str | None]:
    file_path = tmp_path / "pong.txt"
    if kind == "file":
        file_path.write_text("pong")

    @alias_ctx(read="download")
    @response_ctx(headers={"X-Table": "table"})
    class Widget:
        @op_ctx(alias="download", target="custom", arity="collection", persist="none")
        @response_ctx(kind=kind)
        def download(cls, ctx):
            if kind == "auto":
                return as_json({"pong": True})
            if kind == "json":
                return as_json({"pong": True}, envelope=False)
            if kind == "html":
                return as_html("<h1>pong</h1>")
            if kind == "text":
                return as_text("pong")
            if kind == "file":
                return as_file(file_path)
            if kind == "stream":
                return as_stream([b"p", b"o", b"n", b"g"])
            if kind == "redirect":
                return as_redirect("/redirected")
            return {"pong": True}

    specs = list(collect_decorated_ops(Widget))
    build_schemas(Widget, specs)
    build_hooks(Widget, specs)
    build_handlers(Widget, specs)
    runtime_plan.attach_atoms_for_model(Widget, {})
    build_rest(Widget, specs)
    register_rpc(Widget, specs)
    return Widget, (file_path if kind == "file" else None)


def build_model_for_jinja_response(tmp_path) -> type:
    tpl = tmp_path / "hello.html"
    tpl.write_text("<h1>{{ name }}</h1>")

    @alias_ctx(read="download")
    @response_ctx(headers={"X-Table": "table"})
    class Widget:
        @op_ctx(alias="download", target="custom", arity="collection", persist="none")
        async def download(cls, ctx):
            html = await render_template(
                name="hello.html",
                context={"name": "World"},
                search_paths=[str(tmp_path)],
            )
            return as_html(html)

    specs = list(collect_decorated_ops(Widget))
    build_schemas(Widget, specs)
    build_hooks(Widget, specs)
    build_handlers(Widget, specs)
    runtime_plan.attach_atoms_for_model(Widget, {})
    build_rest(Widget, specs)
    register_rpc(Widget, specs)
    return Widget
