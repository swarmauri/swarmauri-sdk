# peagen/transport/ws_server.py
from __future__ import annotations
import json, asyncio
from fastapi import APIRouter, WebSocket
from redis.asyncio import Redis
from peagen.gateway.runtime_cfg import get_settings

settings = get_settings()
print(settings)
print(settings.redis_url)
redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
router = APIRouter()

@router.websocket("/ws/tasks")
async def ws_tasks(ws: WebSocket):
    """Bridge Redis → WebSocket so any GUI/TUI can stream task events."""
    await ws.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe("task:update")
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await ws.send_text(msg["data"])
    finally:
        await pubsub.unsubscribe("task:update")
