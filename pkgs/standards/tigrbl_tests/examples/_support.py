from __future__ import annotations

import asyncio
import socket
from typing import Tuple

import httpx
import uvicorn

from tigrbl.system import stop_uvicorn_server


def pick_unique_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def start_uvicorn(
    app,
    *,
    host: str = "127.0.0.1",
    port: int,
    log_level: str = "warning",
) -> Tuple[str, uvicorn.Server, asyncio.Task]:
    config = uvicorn.Config(app, host=host, port=port, log_level=log_level)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve(), name=f"uvicorn-{host}:{port}")
    base_url = f"http://{host}:{port}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        deadline = asyncio.get_event_loop().time() + 5.0
        while True:
            try:
                response = await client.get(f"{base_url}/healthz")
                if response.status_code < 500:
                    break
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"Timed out waiting for {base_url}/healthz")

    return base_url, server, task


async def stop_uvicorn(server: uvicorn.Server, task: asyncio.Task) -> None:
    await stop_uvicorn_server(server, task)
