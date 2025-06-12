"""WebSocket client utilities for the Peagen TUI."""

from __future__ import annotations

import json
from typing import Awaitable, Callable, Dict, List

import websockets


class TaskStreamClient:
    """Consume gateway events from ``/ws/tasks``."""

    def __init__(self, ws_url: str) -> None:
        self.ws_url = ws_url
        self.tasks: Dict[str, dict] = {}
        self.workers: Dict[str, dict] = {}
        self.queues: Dict[str, int] = {}
        self._callbacks: List[Callable[[dict], Awaitable[None]]] = []

    def on_event(self, cb: Callable[[dict], Awaitable[None]]) -> None:
        """Register *cb* to be awaited for every event."""

        self._callbacks.append(cb)

    async def listen(self) -> None:
        try:
            async with websockets.connect(self.ws_url) as ws:
                async for message in ws:
                    try:
                        event = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                    ev_type = event.get("type")
                    data = event.get("data")
                    if not isinstance(data, dict):
                        continue
                    if ev_type == "task.update":
                        tid = data.get("id")
                        if tid:
                            if "time" in event:
                                data["time"] = event["time"]
                            self.tasks[tid] = data
                    elif ev_type == "worker.update":
                        wid = data.get("id")
                        if wid:
                            self.workers[wid] = data
                    elif ev_type == "queue.update":
                        pool = data.get("pool")
                        if pool:
                            self.queues[pool] = int(data.get("length", 0))
                    for cb in self._callbacks:
                        await cb(event)
        except (OSError, websockets.exceptions.InvalidStatus):
            # connection failed; just ignore
            pass
