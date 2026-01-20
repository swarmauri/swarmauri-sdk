"""Utilities for running uvicorn during tests or tooling."""

from __future__ import annotations

import asyncio

import uvicorn


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
        if not task.done():
            task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return
