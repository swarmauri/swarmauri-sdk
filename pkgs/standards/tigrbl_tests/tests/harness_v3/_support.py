"""Shared helpers for the v3 TDD harness.

These tests intentionally exercise the *runtime-owned routing* path:
- Run a real uvicorn server.
- Hit the server with HTTP (REST + JSON-RPC).

Design goals:
- Minimal dependencies.
- Deterministic, local-only.
- Clear failure modes.
"""

from __future__ import annotations

import asyncio
import socket
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Tuple

import httpx
import uvicorn


def pick_unique_port() -> int:
    """Return an OS-assigned free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def wait_until_listening(base_url: str, *, timeout_s: float = 5.0) -> None:
    """Poll until the server accepts connections."""
    deadline = asyncio.get_event_loop().time() + timeout_s
    last_exc: Exception | None = None

    async with httpx.AsyncClient(base_url=base_url, timeout=0.5) as client:
        while asyncio.get_event_loop().time() < deadline:
            try:
                # Any response (even 404/501) means the server is up.
                await client.get("/")
                return
            except Exception as exc:  # pragma: no cover
                last_exc = exc
                await asyncio.sleep(0.05)

    raise RuntimeError(f"uvicorn did not start listening at {base_url}: {last_exc!r}")


async def start_uvicorn(
    app: Any, *, port: int
) -> Tuple[str, uvicorn.Server, asyncio.Task[None]]:
    """Start uvicorn in-process (async task) and return (base_url, server, task)."""
    cfg = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        lifespan="off",  # tests drive explicit init; keep lifecycle deterministic
    )
    server = uvicorn.Server(cfg)

    task = asyncio.create_task(server.serve())
    base_url = f"http://127.0.0.1:{port}"
    await wait_until_listening(base_url)
    return base_url, server, task


async def stop_uvicorn(server: uvicorn.Server, task: asyncio.Task[None]) -> None:
    """Stop a running uvicorn server started via start_uvicorn."""
    server.should_exit = True
    try:
        await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:  # pragma: no cover
        task.cancel()
        raise


@asynccontextmanager
async def running_server(app: Any, *, port: int | None = None) -> AsyncIterator[str]:
    """Async context manager that yields the base_url of a live uvicorn server."""
    port = pick_unique_port() if port is None else port
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        yield base_url
    finally:
        await stop_uvicorn(server, task)
