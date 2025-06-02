from fastapi import FastAPI, WebSocket, Depends
from ..pools.manager import PoolManager
from ..tasks.queue import TaskQueue
from ..models import User, Role
from ..config import settings
import asyncio, json, logging
from redis.asyncio import Redis

log = logging.getLogger(__name__)
app = FastAPI(title="DQueue API")

queue = TaskQueue()


def current_user() -> User:  # stub – plug in JWT or OAuth later
    return User(username="demo", role=Role.admin)


# ───────────────────────────────── pools ─────────────────────────────────
@app.post("/pools/{name}")
def create_pool(name: str, user: User = Depends(current_user)):
    return PoolManager.create_pool(name, user)


@app.post("/pools/{name}/join")
def join_pool(name: str):
    return PoolManager.join_pool(name, PoolManager.new_member_id())


@app.get("/pools")
def list_pools():
    return PoolManager.list_pools()


# ───────────────────────────────── tasks ────────────────────────────────
@app.post("/pools/{name}/tasks")
async def submit_task(name: str, payload: dict):
    return await queue.enqueue(name, payload)


@app.get("/pools/{name}/tasks")
async def list_tasks(name: str):
    return await queue.list_tasks(name)


@app.delete("/pools/{name}/tasks/{task_id}")
async def cancel_task(name: str, task_id: str):
    return await queue.cancel(task_id, name)


@app.get("/tasks/{task_id}")
async def task_status(task_id: str):
    data = await queue.redis.hget("dqueue:task:index", task_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return json.loads(data)

# ─────────────────────────────── streams ────────────────────────────────
@app.websocket("/ws/tasks")
async def ws_tasks(ws: WebSocket):
    await ws.accept()
    redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("dqueue:task:update")
    async for msg in pubsub.listen():
        if msg["type"] == "message":
            await ws.send_text(msg["data"])
