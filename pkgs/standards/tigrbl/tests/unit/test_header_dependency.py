import asyncio
import threading
import time

import httpx
import pytest
import uvicorn

from tigrbl import op_ctx
from tigrbl.bindings import (
    build_handlers,
    build_hooks,
    build_rest,
    build_schemas,
    register_rpc,
)
from tigrbl.bindings.rest.io_headers import _make_header_dep
from tigrbl.column import IO, S, acol
from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.orm.tables import Base
from tigrbl.response import get_attached_response_spec, response_ctx
from tigrbl.types import App, Integer, Mapped, String


def test_make_header_dep_empty():
    class Model:
        __tigrbl_cols__ = {}

    dep = _make_header_dep(Model, "read")

    async def _run():
        return await dep()

    assert asyncio.run(_run()) == {}


def test_make_header_dep_collects_header():
    class IOObj:
        header_in = "X-Token"
        in_verbs = ("create",)

    class Spec:
        io = IOObj()

    class Model:
        __tigrbl_cols__ = {"token": Spec()}

    dep = _make_header_dep(Model, "create")

    async def _run():
        return await dep(x_token="abc")

    assert asyncio.run(_run()) == {"token": "abc"}


def _build_widget_model():
    Base.metadata.clear()

    class Widget(Base):
        __tablename__ = "widgets"

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        token: Mapped[str | None] = acol(
            storage=S(type_=String, nullable=True),
            io=IO(in_verbs=("echo",), header_in="X-Token"),
        )

        @op_ctx(alias="echo", target="custom", arity="collection", persist="none")
        @response_ctx(headers={"X-Op": "op"})
        def echo(cls, ctx):
            return {"token": ctx["payload"].get("token")}

    specs = list(mro_collect_decorated_ops(Widget))
    build_schemas(Widget, specs)
    build_hooks(Widget, specs)
    build_handlers(Widget, specs)
    build_rest(Widget, specs)
    register_rpc(Widget, specs)
    return Widget


def _run_server(app, port):
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    return server, thread


@pytest.mark.parametrize(
    "header,expected", [({"X-Token": "secret"}, "secret"), ({}, None)]
)
def test_rest_header_dependency(header, expected):
    Widget = _build_widget_model()
    app = App()
    app.include_router(Widget.rest.router)
    server, thread = _run_server(app, 8010)
    try:
        with httpx.Client(base_url="http://127.0.0.1:8010") as client:
            r = client.post("/widget/echo", json={}, headers=header)
        assert r.status_code == 200
        assert r.json() == {"token": expected}
    finally:
        server.should_exit = True
        thread.join()


def test_response_ctx_attaches_header():
    Widget = _build_widget_model()
    spec = get_attached_response_spec(Widget.echo)
    assert spec.headers["X-Op"] == "op"
