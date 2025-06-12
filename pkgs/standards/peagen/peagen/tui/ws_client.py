"""WebSocket client utilities for the Peagen TUI."""

from __future__ import annotations

import json
from typing import Awaitable, Callable, Dict, List

import websockets


class TaskStreamClient:
    """Consume task events from ``/ws/tasks`` and maintain a tasks mapping."""

    def __init__(self, ws_url: str) -> None:
        self.ws_url = ws_url
        self.tasks: Dict[str, dict] = {}
        self._callbacks: List[Callable[[dict], Awaitable[None]]] = []

    def on_event(self, cb: Callable[[dict], Awaitable[None]]) -> None:
        """Register *cb* to be awaited for every task update."""

        self._callbacks.append(cb)

    async def listen(self) -> None:
        async with websockets.connect(self.ws_url) as ws:
            async for message in ws:
                try:
                    event = json.loads(message)
                except json.JSONDecodeError:
                    continue
                data = event.get("data")
                if not isinstance(data, dict):
                    continue
                task_id = data.get("id")
                if task_id:
                    self.tasks[task_id] = data
                for cb in self._callbacks:
                    await cb(data)
