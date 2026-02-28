"""Harness: AppSpec -> uvicorn server E2E.

This is the top-level "works in production" contract.

Contract (TDD):
- A TigrblApp built from AppSpec class attributes can be served via uvicorn.
- REST CRUD works (create, read, list) using runtime-owned routing.
- JSON-RPC works at the configured prefix.
- REST and JSON-RPC share the same underlying storage (parity).
- OpenRPC advertises the configured JSON-RPC prefix.
- Diagnostics live under SYSTEM_PREFIX.

NOTE: This suite is intentionally small but end-to-end.
"""

from __future__ import annotations

import pytest
import httpx

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from ._support import running_server


@pytest.mark.asyncio
async def test_appspec_to_uvicorn_rest_and_rpc_roundtrip() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_e2e_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class HarnessApp(TigrblApp):
        ENGINE = mem(async_=False)
        TABLES = (Widget,)
        JSONRPC_PREFIX = "/rpc-harness"
        SYSTEM_PREFIX = "/system-harness"

    app = HarnessApp()

    # Ensure schema exists before the server starts.
    maybe = app.initialize()
    if maybe is not None:
        # For this harness, ENGINE is sync.
        raise AssertionError("initialize() should be synchronous for mem(async_=False)")

    async with running_server(app) as base_url:
        async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
            # --- System diagnostics live under SYSTEM_PREFIX ---
            r = await client.get("/system-harness/healthz")
            assert r.status_code == 200
            assert r.json().get("ok") is True

            # --- OpenRPC advertises the JSON-RPC prefix ---
            openrpc = (await client.get("/openrpc.json")).json()
            assert openrpc["servers"][0]["url"] == "/rpc-harness"

            # --- REST: create ---
            r = await client.post("/widget", json={"name": "Alpha"})
            assert r.status_code == 201
            alpha = r.json()
            assert alpha["name"] == "Alpha"
            assert "id" in alpha

            # --- REST: read ---
            r = await client.get(f"/widget/{alpha['id']}")
            assert r.status_code == 200
            assert r.json()["id"] == alpha["id"]

            # --- REST: list ---
            r = await client.get("/widget")
            assert r.status_code == 200
            rows = r.json()
            assert isinstance(rows, list)
            assert any(x.get("id") == alpha["id"] for x in rows)

            # --- JSON-RPC: create (at prefix) ---
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "Widget.create",
                "params": {"name": "Beta"},
            }
            r = await client.post("/rpc-harness", json=payload)
            assert r.status_code == 200
            resp = r.json()
            assert resp["jsonrpc"] == "2.0"
            assert resp["id"] == 1
            assert "result" in resp
            beta = resp["result"]
            assert beta["name"] == "Beta"
            assert "id" in beta

            # Parity: REST list sees JSON-RPC created row.
            r = await client.get("/widget")
            assert r.status_code == 200
            rows = r.json()
            assert any(x.get("id") == beta["id"] for x in rows)

            # --- Prefix gating: JSON-RPC body on REST path must not succeed ---
            r = await client.post("/widget", json=payload)
            assert r.status_code >= 400
