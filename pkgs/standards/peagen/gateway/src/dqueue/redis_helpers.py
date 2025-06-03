# dqueue/redis_helpers.py
import json, asyncio
from redis.asyncio import Redis

ACTIVE_SET = "task:active"
FINAL_STATES = {"success", "failed", "cancelled"}

async def save_task(redis: Redis, task, *, ttl_seconds: int = 7 * 24 * 3600):
    key = f"task:{task.id}"
    await redis.set(key, task.model_dump_json())
    if task.status in FINAL_STATES:
        await redis.expire(key, ttl_seconds)
        await redis.srem(ACTIVE_SET, task.id)        # no longer active
    else:
        await redis.sadd(ACTIVE_SET, task.id)        # add/update
