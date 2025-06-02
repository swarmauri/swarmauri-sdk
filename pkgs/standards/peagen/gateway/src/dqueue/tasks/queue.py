from __future__ import annotations
import asyncio, uuid, json
from typing import Dict
from redis.asyncio import Redis
from ..config import settings
from ..models import Task, Status

CHANNEL_TASK_NEW = "dqueue:task:new"
CHANNEL_TASK_UPDATE = "dqueue:task:update"
TASK_INDEX = "dqueue:task:index"      # hash: id -> json

class TaskQueue:
    def __init__(self):
        self.redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)

    # ───────────────── enqueue ─────────────────
    async def enqueue(self, pool: str, payload: dict) -> Task:
        task = Task(id=str(uuid.uuid4()), pool=pool, payload=payload)
        await self.redis.rpush(f"dqueue:{pool}:tasks", task.model_dump_json())
        await self.redis.hset(TASK_INDEX, task.id, task.model_dump_json())
        await self.redis.publish(CHANNEL_TASK_NEW, task.model_dump_json())
        return task

    # ───────────────── cancel ──────────────────
    async def cancel(self, task_id: str, pool: str):
        key = f"dqueue:{pool}:tasks"
        tasks = await self.redis.lrange(key, 0, -1)
        for idx, raw in enumerate(tasks):
            t = Task.model_validate_json(raw)
            if t.id == task_id:
                t.status = Status.cancelled
                await self.redis.lset(key, idx, t.model_dump_json())
                await self.redis.hset(TASK_INDEX, t.id, t.model_dump_json())
                await self.redis.publish(CHANNEL_TASK_UPDATE, t.model_dump_json())
                return t
        raise ValueError("Task not found")

    # ───────────────── list/track ──────────────
    async def list_tasks(self, pool: str):
        ids = await self.redis.lrange(f"dqueue:{pool}:tasks", 0, -1)
        if not ids:
            return []
        return [
            Task.model_validate_json(x)
            for x in (await self.redis.hmget(TASK_INDEX, *[Task.model_validate_json(r).id for r in ids]))
        ]