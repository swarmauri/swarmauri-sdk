# src/dqueue/tasks/worker.py
from __future__ import annotations
import asyncio, logging, json, uuid
from typing import Literal
from redis.asyncio import Redis
from ..config import settings
from ..models import Task, Status
from .queue import CHANNEL_TASK_UPDATE

log = logging.getLogger(__name__)

class Worker:
    def __init__(self, pool: str, id_: str | None = None):
        self.pool = pool
        self.id = id_ or str(uuid.uuid4())[:8]
        self.redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self.queue_key = f"dqueue:{self.pool}:tasks"

    async def run(self) -> None:
        log.info("Worker %s listening on pool %s", self.id, self.pool)
        while True:
            raw = await self.redis.blpop(self.queue_key, timeout=0)   # blocking pop
            if not raw:
                continue  # BLPOP timed out, loop again (timeout=0 means never)
            _, task_json = raw
            task = Task.model_validate_json(task_json)

            # skip cancelled tasks
            if task.status == Status.cancelled:
                continue

            await self._execute(task)

    # ──────────────────────────────────────────────────────────────
    async def _execute(self, task: Task) -> None:
        task.status = Status.running
        await self._publish_update(task)

        # ───── replace with your real workload ─────
        await asyncio.sleep(1)
        task.result = {"echo": task.payload}
        task.status = Status.success
        # ───────────────────────────────────────────

        await self._publish_update(task)

    async def _publish_update(self, task: Task) -> None:
        # persist latest state → hash index
        await self.redis.hset("dqueue:task:index", task.id, task.model_dump_json())
        # broadcast to subscribers
        await self.redis.publish(CHANNEL_TASK_UPDATE, task.model_dump_json())