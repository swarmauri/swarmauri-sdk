"""Utilities for running uvicorn during tests or tooling."""

from __future__ import annotations

import asyncio

import uvicorn


async def _cancel_task(task: asyncio.Task) -> None:
    if task.done():
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        return


async def _close_servers(server: uvicorn.Server) -> None:
    servers = []
    primary = getattr(server, "server", None)
    if primary is not None:
        servers.append(primary)
    extra = getattr(server, "servers", None)
    if extra:
        servers.extend(extra)
    for srv in servers:
        close = getattr(srv, "close", None)
        if callable(close):
            close()
        wait_closed = getattr(srv, "wait_closed", None)
        if callable(wait_closed):
            await wait_closed()


async def stop_uvicorn_server(
    server: uvicorn.Server,
    task: asyncio.Task,
    *,
    timeout: float = 5.0,
) -> None:
    """Request uvicorn shutdown and ensure the task exits."""
    if task.done():
        return

    server.should_exit = True
    try:
        await asyncio.wait_for(task, timeout=timeout)
        return
    except asyncio.TimeoutError:
        server.force_exit = True
        shutdown = getattr(server, "shutdown", None)
        if callable(shutdown):
            try:
                await asyncio.wait_for(shutdown(), timeout=timeout)
            except asyncio.TimeoutError:
                pass
        await _close_servers(server)
        await _cancel_task(task)
