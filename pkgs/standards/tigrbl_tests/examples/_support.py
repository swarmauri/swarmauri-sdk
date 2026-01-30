from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass

import httpx
import uvicorn

from tigrbl.system import stop_uvicorn_server
from tigrbl.types import App


@dataclass
class UvicornHandle:
    base_url: str
    server: uvicorn.Server
    task: asyncio.Task


def pick_unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def run_uvicorn_app(app: App, *, port: int) -> UvicornHandle:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    base_url = f"http://127.0.0.1:{port}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        deadline = asyncio.get_event_loop().time() + 5.0
        while True:
            try:
                response = await client.get(base_url + "/healthz")
                if response.status_code < 500:
                    break
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"Timed out waiting for {base_url}/healthz")
    return UvicornHandle(base_url=base_url, server=server, task=task)


async def stop_server(handle: UvicornHandle) -> None:
    await stop_uvicorn_server(handle.server, handle.task)
