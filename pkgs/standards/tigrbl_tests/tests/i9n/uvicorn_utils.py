import asyncio
import socket
from typing import Tuple

import uvicorn
from tigrbl.system import stop_uvicorn_server as stop_uvicorn_server_impl


async def run_uvicorn_in_task(
    app, *, host: str = "127.0.0.1", log_level: str = "warning"
) -> Tuple[str, uvicorn.Server, asyncio.Task]:
    """Start a uvicorn server on an available port and wait for startup."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        _, port = sock.getsockname()

    cfg = uvicorn.Config(app, host=host, port=port, log_level=log_level)
    server = uvicorn.Server(cfg)
    task = asyncio.create_task(server.serve())

    async def _wait_until_started() -> None:
        while not server.started:
            if task.done():
                exc = task.exception()
                raise RuntimeError("Uvicorn failed to start") from exc
            await asyncio.sleep(0.05)

    try:
        await asyncio.wait_for(_wait_until_started(), timeout=10)
    except Exception:
        server.should_exit = True
        if not task.done():
            task.cancel()
        raise

    return f"http://{host}:{port}", server, task


async def stop_uvicorn_server(server: uvicorn.Server, task: asyncio.Task) -> None:
    """Stop a uvicorn server started with run_uvicorn_in_task."""
    await stop_uvicorn_server_impl(server, task)
