# peagen/transport/ws_server.py
from __future__ import annotations

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from redis.asyncio import Redis
from peagen.gateway.runtime_cfg import settings
from peagen.defaults import READY_QUEUE, PUBSUB_CHANNEL
import json

redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
router = APIRouter()


async def _send_snapshot(ws: WebSocket) -> None:
    """Send the current state to a newly connected client."""

    # pools & queue lengths
    pools = await redis.smembers("pools")
    for pool in pools:
        qlen = len(await redis.lrange(f"{READY_QUEUE}:{pool}", 0, -1))
        await ws.send_text(
            json.dumps({"type": "queue.update", "data": {"pool": pool, "length": qlen}})
        )

    # active workers
    for key in await redis.keys("worker:*"):
        worker = await redis.hgetall(key)
        wid = key.split(":", 1)[1]
        await ws.send_text(
            json.dumps({"type": "worker.update", "data": {"id": wid, **worker}})
        )

    # persisted tasks
    for key in await redis.keys("task:*"):
        blob = await redis.hget(key, "blob")
        if blob:
            await ws.send_text(
                json.dumps({"type": "task.update", "data": json.loads(blob)})
            )


@router.websocket("/ws/tasks")
async def ws_tasks(ws: WebSocket):
    """Bridge Redis → WebSocket so any GUI/TUI can stream task events."""
    await ws.accept()
    await _send_snapshot(ws)
    pubsub = redis.pubsub()
    await pubsub.subscribe(PUBSUB_CHANNEL)
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                try:
                    await ws.send_text(msg["data"])
                except WebSocketDisconnect:
                    break
    finally:
        await pubsub.unsubscribe(PUBSUB_CHANNEL)
