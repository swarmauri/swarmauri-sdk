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

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Protocol

from tigrbl import get_schema
from tigrbl.orm.tables.status import Status
from tigrbl_client import TigrblClient

from peagen.defaults import READY_QUEUE, TASK_KEY, TASK_TTL, WORKER_KEY, WORKER_TTL
from peagen.orm import Task, Worker


# Define protocol for logger to avoid circular imports
class Logger(Protocol):
    def info(self, msg: str, *args: Any) -> None: ...
    def warning(self, msg: str, *args: Any) -> None: ...
    def error(self, msg: str, *args: Any) -> None: ...


# ───────────────── Pydantic schema handles ─────────────────────────────
TaskCreate = get_schema(Task, "create")
TaskRead = get_schema(Task, "read")
WorkerRead = get_schema(Worker, "read")


# ───────────────────────── Queue helpers ──────────────────────────────
def _task_cache_key(tid: str) -> str:
    return TASK_KEY.format(tid)


def _worker_cache_key(worker_id: str) -> str:
    return WORKER_KEY.format(worker_id)


# ─────────── Task queue helpers ────────────────────────────────────────
async def pop_next_task(
    queue, log: Logger, pool: str, timeout: int = 5
) -> Optional[TaskCreate]:
    """
    Blocking-pop the next TaskCreate JSON blob from the pool queue.
    Returns None on timeout.
    """
    qname = f"{READY_QUEUE}:{pool}"
    res = await queue.blpop(qname, timeout=timeout)
    if res is None:
        return None

    _key, raw_json = res  # Redis BLPOP format
    try:
        return TaskCreate.model_validate_json(raw_json)
    except Exception as exc:  # noqa: BLE001
        log.error("invalid Task blob on queue %s: %s", pool, exc)
        return None


# ─────────── Worker registry helpers ───────────────────────────────────
async def get_live_workers_by_pool(queue, pool: str) -> List[Dict[str, Any]]:
    """
    Return live worker hashes for *pool* (TTL-filtered).
    """
    keys = await queue.keys("worker:*")
    now = int(time.time())
    workers: List[Dict[str, Any]] = []

    for k in keys:
        blob = await queue.hgetall(k)
        if not blob:
            continue
        if now - int(blob.get("last_seen", 0)) > WORKER_TTL:
            continue  # stale
        if blob.get("pool") != pool:
            continue

        wid = k.split(":", 1)[1]
        workers.append({"id": wid, **blob})
    return workers


def pick_worker(
    workers: List[Dict[str, Any]], action: Optional[str]
) -> Optional[Dict[str, Any]]:
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


async def remove_worker(queue, worker_id: str) -> None:
    """
    Expire the worker's registry entry immediately and broadcast update.
    """
    from ._publish import _publish_event

    await queue.expire(_worker_cache_key(worker_id), 0)
    await _publish_event(queue, "worker.update", {"id": worker_id, "removed": True})


# ─────────── Dispatch helper (Tigrbl-native) ─────────────────────────
async def dispatch_work(
    task: TaskCreate, worker: Dict[str, Any], log: Logger = None
) -> bool:
    """
    Invoke *work.start* on the chosen worker using TigrblClient.

    Returns:
        True  – RPC returned without error
        False – transport error or JSON-RPC error
    """
    # ensure we have the worker's /rpc endpoint
    endpoint = worker["url"].rstrip("/")
    if not endpoint.endswith("/rpc"):
        endpoint += "/rpc"

    # TigrblClient is synchronous; run it in a thread so we don't block
    def _sync_rpc() -> bool:
        try:
            with TigrblClient(endpoint) as rpc:
                rpc.call(
                    "Works.create",
                    params={
                        "task_id": str(task.id),
                        "repository_id": str(task.repository_id)
                        if task.repository_id
                        else None,
                    },
                )
            return True
        except Exception as exc:  # includes HTTP & JSON-RPC errors
            if log:
                log.warning("dispatch to %s failed: %s", worker["id"], exc)
            return False

    return await asyncio.to_thread(_sync_rpc)


# ───────────────────────── Redis helpers ──────────────────────────────
async def _save_task(queue, task: TaskRead) -> None:
    """Upsert *task* (TaskRead model) into Redis and refresh its TTL."""
    key = _task_cache_key(str(task.id))
    blob_json = json.dumps(task.model_dump(mode="json"))
    await queue.hset(
        key,
        mapping={"blob": blob_json, "status": str(task.status)},
    )
    await queue.expire(key, TASK_TTL)


async def _load_task(queue, tid: str) -> TaskRead | None:
    data = await queue.hget(_task_cache_key(tid), "blob")
    return TaskRead.model_validate_json(data) if data else None


# ───────────────────────── misc utilities ─────────────────────────────
async def _finalize_parent_tasks(queue, child_id: str) -> None:
    """
    Check if any parent tasks have all their children completed.
    If so, mark the parent as SUCCESS.
    """
    from ._publish import _publish_task

    keys = await queue.keys("task:*")
    for key in keys:
        blob = await queue.hget(key, "blob")
        if not blob:
            continue

        parent = TaskRead.model_validate_json(blob)
        children = parent.result.get("children", []) if parent.result else []

        if child_id not in children:
            continue

        all_done = True
        for cid in children:
            child = await _load_task(queue, cid)
            if child is None or not Status.is_terminal(child.status):
                all_done = False
                break

        if all_done and parent.status != Status.SUCCESS:
            parent = parent.model_copy(
                update={"status": Status.SUCCESS, "last_modified": time.time()}
            )
            await _save_task(queue, parent)
            await _publish_task(queue, parent)


async def _fail_task(queue, task: TaskRead, exc: Exception, log: Logger) -> None:
    """
    Mark *task* as failed, persist it to Redis, and fan-out an update.

    Args:
        task:     a TaskRead Pydantic instance (cached copy or DB fetch).
        exc:      the exception that caused the failure.
    """
    from ._publish import _publish_task

    failed = task.model_copy(
        update={
            "status": Status.FAILED,
            "result": {"error": str(exc)},
            "last_modified": time.time(),
        }
    )

    await _save_task(queue, failed)
    await _publish_task(queue, failed)
    await _finalize_parent_tasks(queue, str(failed.id))

    log.info("task %s failed – %s", failed.id, exc)
