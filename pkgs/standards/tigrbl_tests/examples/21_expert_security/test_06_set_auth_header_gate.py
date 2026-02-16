"""Lesson 21.6: Header-based set_auth gate for REST and JSON-RPC.

This example demonstrates ``set_auth`` with a header-driven authn dependency
that supports two credential tiers:

* ``X-Admin-Key`` for full admin access.
* Session token for limited public access.

It also shows how to keep selected routes/methods anonymous by combining the
header gate with ``__tigrbl_allow_anon__``.
"""

import inspect

import httpx
import pytest
from tigrbl.security import HTTPAuthorizationCredentials, HTTPBearer

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, HTTPException, Request, Security, String


ADMIN_KEY = "admin-secret"
PUBLIC_SESSION_TOKEN = "public-session-token"


@pytest.mark.asyncio
async def test_set_auth_header_gate_for_rest_paths() -> None:
    """Show REST access control with admin/public headers plus anon paths."""

    class HeaderGateRestWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_header_gate_rest_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    bearer = HTTPBearer(auto_error=False)

    def _rest_method_id(request: Request) -> str | None:
        verb_to_alias = {"GET": "list", "POST": "create"}
        alias = verb_to_alias.get(request.method.upper())
        if not alias:
            return None
        if request.path != f"/{HeaderGateRestWidget.__name__.lower()}":
            return None
        return f"{HeaderGateRestWidget.__name__}.{alias}"

    async def header_gate(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer),
    ) -> dict[str, str] | None:
        admin_key = request.headers.get("X-Admin-Key") or request.headers.get(
            "x-admin-key"
        )
        if admin_key == ADMIN_KEY:
            user = {"role": "admin"}
            request.state.user = user
            return user

        session_token = credentials.credentials if credentials else None
        if session_token == PUBLIC_SESSION_TOKEN:
            method_id = _rest_method_id(request)
            if method_id in app._allow_anon_ops:
                user = {"role": "public", "token": session_token}
                request.state.user = user
                return user

            raise HTTPException(
                status_code=403,
                detail="Public session token cannot access this REST path",
            )

        method_id = _rest_method_id(request)
        if method_id is not None and method_id not in app._allow_anon_ops:
            raise HTTPException(
                status_code=401, detail="Missing authentication headers"
            )

        return None

    app.set_auth(authn=header_gate, optional_authn_dep=header_gate, allow_anon=False)
    app.include_model(HeaderGateRestWidget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        list_path = f"/{HeaderGateRestWidget.__name__.lower()}"

        anon_list = await client.get(list_path)
        assert anon_list.status_code == 200

        anon_create = await client.post(list_path, json={"name": "anon-create"})
        assert anon_create.status_code == 401

        public_list = await client.get(
            list_path,
            headers={"Authorization": f"Bearer {PUBLIC_SESSION_TOKEN}"},
        )
        assert public_list.status_code == 200

        public_create = await client.post(
            list_path,
            json={"name": "public-create"},
            headers={"Authorization": f"Bearer {PUBLIC_SESSION_TOKEN}"},
        )
        assert public_create.status_code == 403

        admin_create = await client.post(
            list_path,
            json={"name": "admin-create"},
            headers={"X-Admin-Key": ADMIN_KEY},
        )
        assert admin_create.status_code in {200, 201}
        assert admin_create.json()["name"] == "admin-create"

    await stop_uvicorn(server, task)


@pytest.mark.asyncio
async def test_set_auth_header_gate_for_rpc_methods() -> None:
    """Show JSON-RPC access control with admin/public headers plus anon methods."""

    class HeaderGateRpcWidget(Base, GUIDPk):
        __tablename__ = "lesson_security_header_gate_rpc_widget"
        __allow_unmapped__ = True
        __tigrbl_allow_anon__ = ("list",)

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    bearer = HTTPBearer(auto_error=False)

    async def header_gate(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer),
    ) -> dict[str, str] | None:
        admin_key = request.headers.get("X-Admin-Key") or request.headers.get(
            "x-admin-key"
        )
        if admin_key == ADMIN_KEY:
            user = {"role": "admin"}
            request.state.user = user
            return user

        session_token = credentials.credentials if credentials else None
        if session_token == PUBLIC_SESSION_TOKEN:
            if request.path == "/rpc":
                body = await request.json()
                calls = body if isinstance(body, list) else [body]
                methods = {
                    call.get("method")
                    for call in calls
                    if isinstance(call, dict) and isinstance(call.get("method"), str)
                }
                if methods and methods.issubset(app._allow_anon_ops):
                    user = {"role": "public", "token": session_token}
                    request.state.user = user
                    return user

            raise HTTPException(
                status_code=403,
                detail="Public session token cannot access this RPC method",
            )

        return None

    app.set_auth(authn=header_gate, optional_authn_dep=header_gate, allow_anon=False)
    app.include_model(HeaderGateRpcWidget)

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    app.mount_jsonrpc(prefix="/rpc")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        anon_list = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": f"{HeaderGateRpcWidget.__name__}.list",
                "params": {},
            },
        )
        assert anon_list.status_code == 200
        assert "result" in anon_list.json()

        anon_create = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": f"{HeaderGateRpcWidget.__name__}.create",
                "params": {"name": "anon-rpc-create"},
            },
        )
        assert anon_create.status_code == 200
        assert anon_create.json()["error"]["code"] == -32001

        public_list = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": f"{HeaderGateRpcWidget.__name__}.list",
                "params": {},
            },
            headers={"Authorization": f"Bearer {PUBLIC_SESSION_TOKEN}"},
        )
        assert public_list.status_code == 200
        assert "result" in public_list.json()

        public_create = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": f"{HeaderGateRpcWidget.__name__}.create",
                "params": {"name": "public-rpc-create"},
            },
            headers={"Authorization": f"Bearer {PUBLIC_SESSION_TOKEN}"},
        )
        assert public_create.status_code == 200

        admin_create = await client.post(
            "/rpc",
            json={
                "jsonrpc": "2.0",
                "id": 5,
                "method": f"{HeaderGateRpcWidget.__name__}.create",
                "params": {"name": "admin-rpc-create"},
            },
            headers={"X-Admin-Key": ADMIN_KEY},
        )
        assert admin_create.status_code == 200
        assert admin_create.json()["error"]["code"] == -32001

    await stop_uvicorn(server, task)
