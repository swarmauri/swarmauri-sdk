from __future__ import annotations

import httpx
import pytest

from tigrbl import Base, TigrblApp, hook_ctx, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import App, Integer, Mapped, String

from ..uvicorn_support import run_uvicorn_in_task, stop_uvicorn_server


@pytest.mark.asyncio
async def test_custom_op_with_hook() -> None:
    class Widget(Base):
        __tablename__ = "hook_ops_widgets"
        __resource__ = "widget"

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        __tigrbl_cols__ = {"id": id, "name": name}

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"pong": True}

        @hook_ctx(ops="ping", phase="POST_HANDLER")
        async def add_meta(cls, ctx):
            ctx["result"]["meta"] = "hooked"

    app = App()
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget, prefix="")
    await api.initialize()
    app.include_router(api.router)

    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/widget/ping")
        assert response.status_code == 200
        assert response.json()["meta"] == "hooked"
    finally:
        await stop_uvicorn_server(server, task)
