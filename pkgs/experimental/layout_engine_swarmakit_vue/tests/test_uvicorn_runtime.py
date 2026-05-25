from __future__ import annotations

import asyncio
import socket

import httpx
import pytest
import uvicorn

from layout_engine.authoring.ctx.builder import TableCtx

from layout_engine_swarmakit_vue import (
    SwarmakitAvatar,
    SwarmakitDataGrid,
    SwarmakitNotification,
    SwarmakitProgressBar,
    create_swarmakit_fastapi_app,
)


def _build_demo_table() -> TableCtx:
    table = TableCtx()
    row = table.row()
    row.col(size="s").add(
        SwarmakitAvatar(
            "avatar.demo", initials="SD", image_src="https://cdn.example/demo.png"
        ),
    )
    row.col(size="m").add(
        SwarmakitNotification(
            "notification.demo",
            message="Swarmakit Vue is online.",
            notification_type="success",
        ),
        SwarmakitProgressBar("progress.demo", progress=64),
    )
    row.col(size="l").add(
        SwarmakitDataGrid(
            "grid.demo",
            headers=["Name", "Status"],
            data=[["Orchestrator", "Ready"], ["Renderer", "Ready"]],
        ),
    )
    return table


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.mark.asyncio
async def test_uvicorn_serves_swarmakit_page() -> None:
    table = _build_demo_table()
    app = create_swarmakit_fastapi_app(
        table, title="Swarmakit Demo", width=800, height=600
    )
    port = _find_free_port()

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    try:
        for _ in range(50):
            if server.started:
                break
            await asyncio.sleep(0.1)
        assert server.started, "Uvicorn server did not start in time"

        async with httpx.AsyncClient() as client:
            base_url = f"http://127.0.0.1:{port}"
            response = await client.get(base_url + "/")
            assert response.status_code == 200
            assert "@swarmakit/vue" in response.text
            assert "swarmakit-manifest" in response.text

            manifest_resp = await client.get(base_url + "/manifest.json")
            assert manifest_resp.status_code == 200
            payload = manifest_resp.json()
            modules = {tile["component"]["module"] for tile in payload["tiles"]}
            exports = {tile["component"]["export"] for tile in payload["tiles"]}
            assert "@swarmakit/vue" in modules
            assert {"Avatar", "DataGrid"}.issubset(exports)
    finally:
        server.should_exit = True
        await asyncio.wait_for(server_task, timeout=5)
