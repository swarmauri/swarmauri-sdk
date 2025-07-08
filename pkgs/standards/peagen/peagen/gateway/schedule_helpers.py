"""
gateway.scheduler_helper
────────────────────────
Core scheduling loop utilities:

• pop_next_task(pool)         –   BLPOP from Redis queue → TaskCreate model
• pick_worker(pool, action)   –   choose first live worker advertising the action
• dispatch(work, worker_url)  –   POST /rpc work.start to the worker
• remove_worker(worker_id)    –   immediate TTL expiry + event fan-out
• live_workers_by_pool(pool)  –   cached list used by dashboards & pick_worker
"""

from __future__ import annotations
import json, time, uuid, httpx, asyncio
from typing import Dict, Any, Optional, List

from autoapi.v2   import AutoAPI
from peagen.orm   import Task, Worker
from peagen.defaults import READY_QUEUE, WORKER_KEY, WORKER_TTL
from .            import queue, log
from ._publish    import _publish_event, _publish_queue_length

# ───────────────── Pydantic schema handles ─────────────────────────────
TaskCreate = AutoAPI.get_schema(Task, "create")
TaskRead   = AutoAPI.get_schema(Task, "read")
WorkerRead = AutoAPI.get_schema(Worker, "read")

# ─────────── Task queue helpers ────────────────────────────────────────
async def pop_next_task(pool: str, timeout: int = 5) -> Optional[TaskCreate]:
    """
    Blocking-pop the next TaskCreate JSON blob from the pool queue.
    Returns None on timeout.
    """
    qname = f"{READY_QUEUE}:{pool}"
    res = await queue.blpop(qname, timeout=timeout)
    if res is None:
        return None

    _key, raw_json = res                 # Redis BLPOP format
    try:
        return TaskCreate.model_validate_json(raw_json)
    except Exception as exc:             # noqa: BLE001
        log.error("invalid Task blob on queue %s: %s", pool, exc)
        return None


# ─────────── Worker registry helpers ───────────────────────────────────
async def _cache_key(worker_id: str) -> str:
    return WORKER_KEY.format(worker_id)


async def live_workers_by_pool(pool: str) -> List[Dict[str, Any]]:
    """
    Return live worker hashes for *pool* (TTL-filtered).
    """
    keys     = await queue.keys("worker:*")
    now      = int(time.time())
    workers: List[Dict[str, Any]] = []

    for k in keys:
        blob = await queue.hgetall(k)
        if not blob:
            continue
        if now - int(blob.get("last_seen", 0)) > WORKER_TTL:
            continue                     # stale
        if blob.get("pool") != pool:
            continue

        wid = k.split(":", 1)[1]
        workers.append({"id": wid, **blob})
    return workers


def _pick_worker(workers: List[Dict[str, Any]], action: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Return the first worker advertising *action* (handler name), or None.
    """
    if action is None:
        return None
    for w in workers:
        raw_handlers = w.get("handlers", [])
        if isinstance(raw_handlers, str):
            try:
                raw_handlers = json.loads(raw_handlers)
            except Exception:  # noqa: BLE001
                raw_handlers = []
        if action in raw_handlers:
            return w
    return None


async def remove_worker(worker_id: str) -> None:
    """
    Expire the worker's registry entry immediately and broadcast update.
    """
    await queue.expire(await _cache_key(worker_id), 0)
    await _publish_event("worker.update", {"id": worker_id, "removed": True})


# ─────────── Dispatch helper ───────────────────────────────────────────
async def dispatch_work(task: TaskCreate, worker: Dict[str, Any]) -> bool:
    """
    Send `work.start` RPC to *worker*. Returns True on 200 OK JSON-RPC success,
    False otherwise (network error, non-2xx, JSON-RPC error etc.).
    """
    url = worker["url"]
    if not url.endswith("/rpc"):
        url = url.rstrip("/") + "/rpc"

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "work.start",
        "params": {
            "task_id": str(task.id),
            # work_id is obtained in handler; send idempotent key here
            "repository_id": str(task.repository_id) if task.repository_id else None,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as cl:
            resp = await cl.post(url, json=payload)
        if resp.status_code != 200:
            log.warning("dispatch failed %s → %s (HTTP %s)", task.id, worker["id"], resp.status_code)
            return False
        body = resp.json()
        if "error" in body:
            log.warning("worker %s error: %s", worker["id"], body["error"])
            return False
        log.info("task %s dispatched to worker %s", task.id, worker["id"])
        return True
    except Exception as exc:             # noqa: BLE001
        log.warning("dispatch exception to %s: %s", worker["id"], exc)
        return False

