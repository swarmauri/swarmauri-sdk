from __future__ import annotations

import httpx
import pytest

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import App, Integer, Mapped, String

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


@pytest.mark.asyncio
async def test_hook_modifies_response() -> None:
    class Item(Base):
        __tablename__ = "hook_items"
        __resource__ = "item"

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

        @hook_ctx(ops="create", phase="POST_RESPONSE")
        async def add_flag(cls, ctx):
            ctx["response"].result["hooked"] = True

    app = App()
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Item, prefix="")
    await api.initialize()
    app.include_router(api.router)

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/item", json={"name": "Hook"})
        assert response.status_code == 201
        assert response.json()["hooked"] is True
    finally:
        await stop_uvicorn(server, task)
