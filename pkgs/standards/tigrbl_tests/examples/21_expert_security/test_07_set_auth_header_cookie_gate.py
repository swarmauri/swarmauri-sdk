"""Lesson 21.7: Gate every call with a header-or-cookie security dependency.

This example shows one ``set_auth`` dependency that accepts either:

* ``X-Admin-Key`` header for admin access.
* ``sid`` session cookie for user access.

With ``allow_anon=False`` and no ``__tigrbl_allow_anon__`` overrides, all REST
and JSON-RPC calls are protected by this dependency.
"""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.requests import Request
from tigrbl.runtime.status import HTTPException
from tigrbl.types import Column, String

ADMIN_KEY = "admin-secret"
SESSION_COOKIE = "session-secret"


@pytest.mark.asyncio
async def test_set_auth_header_cookie_gate_for_rest_and_rpc() -> None:
    """Require either admin header or session cookie on every call."""

    class HeaderCookieGateWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_header_cookie_gate_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))

    async def header_cookie_gate(request: Request) -> dict[str, str]:
        admin_key = request.headers.get("X-Admin-Key") or request.headers.get(
            "x-admin-key"
        )
        if admin_key == ADMIN_KEY:
            user = {"role": "admin"}
            request.state.user = user
            return user

        sid = (request.cookies.get("sid") or "").strip()
        if sid == SESSION_COOKIE:
            user = {"role": "session", "sid": sid}
            request.state.user = user
            return user

        raise HTTPException(status_code=401, detail="Missing/invalid auth credentials")

    app.set_auth(
        authn=header_cookie_gate,
        optional_authn_dep=header_cookie_gate,
        allow_anon=False,
    )
    app.include_table(HeaderCookieGateWidget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.mount_jsonrpc(prefix="/rpc")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        list_path = f"/{HeaderCookieGateWidget.__name__.lower()}"

        anon_list = await client.get(list_path)
        assert anon_list.status_code == 401

        sid_list = await client.get(list_path, cookies={"sid": SESSION_COOKIE})
        assert sid_list.status_code == 200

        admin_create = await client.post(
            list_path,
            json={"name": "admin-create"},
            headers={"X-Admin-Key": ADMIN_KEY},
        )
        assert admin_create.status_code in {200, 201}

        anon_rpc = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": f"{HeaderCookieGateWidget.__name__}.list",
                "params": {},
            },
        )
        assert anon_rpc.status_code == 200
        assert anon_rpc.json()["error"]["code"] == -32001

        sid_rpc = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": f"{HeaderCookieGateWidget.__name__}.list",
                "params": {},
            },
            cookies={"sid": SESSION_COOKIE},
        )
        assert sid_rpc.status_code == 200
        assert "result" in sid_rpc.json()

    await stop_uvicorn(server, task)
