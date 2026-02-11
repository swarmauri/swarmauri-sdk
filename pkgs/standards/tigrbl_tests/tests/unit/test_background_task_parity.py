from __future__ import annotations

import asyncio

from starlette.background import BackgroundTask as StarletteBackgroundTask

from tigrbl.transport.background import BackgroundTask


def test_background_task_sync_parity() -> None:
    events: list[tuple[str, int]] = []

    def record(name: str, value: int) -> None:
        events.append((name, value))

    tigrbl_task = BackgroundTask(record, "task", 1)
    starlette_task = StarletteBackgroundTask(record, "task", 2)

    asyncio.run(tigrbl_task())
    asyncio.run(starlette_task())

    assert events == [("task", 1), ("task", 2)]


def test_background_task_async_parity() -> None:
    events: list[str] = []

    async def record_async(name: str) -> None:
        events.append(name)

    tigrbl_task = BackgroundTask(record_async, "tigrbl")
    starlette_task = StarletteBackgroundTask(record_async, "starlette")

    asyncio.run(tigrbl_task())
    asyncio.run(starlette_task())

    assert events == ["tigrbl", "starlette"]
