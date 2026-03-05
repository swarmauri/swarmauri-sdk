from __future__ import annotations

import asyncio
import json
import ssl
from typing import Any

import httpx
import pytest
from tigrbl import Request
from tigrbl import TigrblApp
from tigrbl import TigrblRouter
from tigrbl_tests.examples._support import pick_unique_port, start_uvicorn, stop_uvicorn


async def _probe_http3_over_quic(host: str, port: int) -> dict[str, Any]:
    try:
        from aioquic.asyncio.client import connect
        from aioquic.quic.configuration import QuicConfiguration
    except Exception:
        return {
            "supported": False,
            "status": 0,
            "error": "aioquic-not-installed",
        }

    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=["h3"],
        verify_mode=ssl.CERT_NONE,
    )

    try:
        async with asyncio.timeout(2.0):
            async with connect(
                host,
                port,
                configuration=configuration,
                wait_connected=True,
            ):
                return {"supported": True, "status": 200, "error": None}
    except Exception as exc:
        return {
            "supported": False,
            "status": 0,
            "error": type(exc).__name__,
        }


@pytest.mark.asyncio
async def test_tigrblapp_uvicorn_h1_h2_h3_behavior() -> None:
    app = TigrblApp()

    router = TigrblRouter()

    @router.get("/echo")
    async def echo(request: Request) -> dict[str, Any]:
        return {
            "method": request.method,
            "x_test": request.headers.get("x-test"),
            "http_version": request.scope.get("http_version"),
        }

    @router.post("/jsonrpc")
    async def jsonrpc(request: Request) -> dict[str, Any]:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id"),
            "result": payload.get("params"),
        }

    app.include_router(router)
    app.attach_diagnostics(prefix="")

    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)

    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
            h1 = await client.get("/echo", headers={"x-test": "h1"})

        h2: httpx.Response | None = None
        h2_error: str | None = None
        try:
            async with httpx.AsyncClient(
                base_url=base_url,
                timeout=5.0,
                http2=True,
            ) as client:
                h2 = await client.get("/echo", headers={"x-test": "h2"})
        except ImportError as exc:
            h2_error = type(exc).__name__

        async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
            rpc = await client.post(
                "/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"msg": "hi"},
                    "id": 1,
                },
            )

        h3 = await _probe_http3_over_quic("127.0.0.1", port)

        out = {
            "http1": {
                "status": h1.status_code,
                "http_version": h1.http_version,
                "body": h1.json(),
            },
            "http2": {
                "status": h2.status_code if h2 else 0,
                "http_version": h2.http_version if h2 else None,
                "body": h2.json() if h2 else None,
                "error": h2_error,
            },
            "jsonrpc": {
                "status": rpc.status_code,
                "http_version": rpc.http_version,
                "body": rpc.json(),
            },
            "http3": h3,
        }

        assert out["http1"]["status"] == 200
        assert out["http1"]["http_version"] == "HTTP/1.1"
        assert out["http1"]["body"]["x_test"] == "h1"

        if h2 is not None:
            assert out["http2"]["status"] == 200
            assert out["http2"]["http_version"] == "HTTP/1.1"
            assert out["http2"]["body"]["x_test"] == "h2"
            assert out["http2"]["error"] is None
        else:
            assert out["http2"]["status"] == 0
            assert out["http2"]["error"] == "ImportError"

        assert out["jsonrpc"]["status"] == 200
        assert out["jsonrpc"]["body"] == {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"msg": "hi"},
        }

        assert out["http3"]["supported"] is False
    finally:
        await stop_uvicorn(server, task)
