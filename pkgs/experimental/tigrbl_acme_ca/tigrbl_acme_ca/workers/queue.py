from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional, Callable, Awaitable

@dataclass
class TaskQueueAdapter:
    """Abstract queue adapter. Runtime should provide a concrete instance in ctx.">
    async def enqueue(self, item: dict) -> None:
        raise NotImplementedError
    async def dequeue(self, *, timeout: Optional[float] = None) -> Optional[dict]:
        raise NotImplementedError

class InMemoryAsyncQueue(TaskQueueAdapter):
    def __init__(self) -> None:
        self._q: asyncio.Queue[dict] = asyncio.Queue()

    async def enqueue(self, item: dict) -> None:
        await self._q.put(item)

    async def dequeue(self, *, timeout: Optional[float] = None) -> Optional[dict]:
        try:
            if timeout is None:
                return await self._q.get()
            return await asyncio.wait_for(self._q.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

def from_ctx(ctx) -> TaskQueueAdapter:
    q = ctx.get("task_queue")
    if q:
        return q
    # Dev fallback
    return InMemoryAsyncQueue()
