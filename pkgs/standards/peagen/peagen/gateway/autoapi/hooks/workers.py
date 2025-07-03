"""
AutoAPI hooks for worker-related operations.
"""

import json
import time
from typing import Any, Dict

import httpx

from peagen.transport.jsonrpc import RPCException

from ... import (
    WORKER_KEY,
    WORKER_TTL,
    log,
    queue,
)
from ...autoapi import api

# ---------------------- Worker Hooks ----------------------


@api.hook(api.Phase.PRE_TX_BEGIN, method="workers.create")
async def pre_worker_create(ctx: Dict[str, Any]) -> None:
    """Pre-processing for worker registration"""
    params = ctx.get("env").params

    # Extract parameters
    worker_id = params.get("id") or params.get("workerId")
    pool = params.get("pool")
    url = params.get("url")
    advertises = params.get("advertises", [])
    handlers = params.get("handlers", [])

    # If handlers not provided, try to fetch from /well-known endpoint
    if not handlers:
        well_known_url = url.replace("/rpc", "/well-known")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(well_known_url)
                if resp.status_code == 200:
                    handlers = resp.json().get("handlers", [])
                    params["handlers"] = handlers
        except Exception as exc:
            log.warning("/well-known fetch failed for %s: %s", worker_id, exc)

    # Validate handlers
    if not handlers:
        raise RPCException(code=-32602, message="worker supports no handlers")

    # Store for post-hook
    ctx["worker_id"] = worker_id
    ctx["pool"] = pool
    ctx["handlers"] = handlers


@api.hook(api.Phase.POST_COMMIT, method="workers.create")
async def post_worker_create(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for worker registration"""
    result = ctx.get("result")
    worker_id = ctx.get("worker_id")
    pool = ctx.get("pool")
    handlers = ctx.get("handlers")

    if result:
        # Format response to match original API
        ctx["result"] = {"ok": True}

        # Log registration
        log.info("worker %s registered (%s) handlers=%s", worker_id, pool, handlers)


@api.hook(api.Phase.PRE_TX_BEGIN, method="workers.update")
async def pre_worker_update(ctx: Dict[str, Any]) -> None:
    """Pre-processing for worker heartbeat"""
    params = ctx.get("env").params

    # Extract parameters
    worker_id = params.get("id") or params.get("workerId")
    pool = params.get("pool")
    url = params.get("url")

    # Check if worker exists
    known = await queue.exists(WORKER_KEY.format(worker_id))
    if not known and not (pool and url):
        log.warning(
            "heartbeat from %s ignored: gateway lacks metadata; send pool+url or re-register",
            worker_id,
        )
        # Set result to avoid further processing
        ctx["result"] = {"ok": False}
        return

    # Update last_seen
    mapping = {"last_seen": int(time.time())}
    if pool:
        mapping["pool"] = pool
        params["pool"] = pool
    if url:
        mapping["url"] = url
        params["url"] = url

    # Store for post-hook
    ctx["worker_id"] = worker_id
    ctx["mapping"] = mapping


@api.hook(api.Phase.POST_COMMIT, method="workers.update")
async def post_worker_update(ctx: Dict[str, Any]) -> None:
    """Post-commit operations for worker heartbeat"""
    result = ctx.get("result")
    worker_id = ctx.get("worker_id")
    mapping = ctx.get("mapping")

    if not result or "result" in ctx:
        return

    # Update Redis
    await queue.hset(WORKER_KEY.format(worker_id), mapping=mapping)
    await queue.expire(WORKER_KEY.format(worker_id), WORKER_TTL)

    # Format response to match original API
    ctx["result"] = {"ok": True}


@api.hook(api.Phase.POST_HANDLER, method="workers.list")
async def post_worker_list(ctx: Dict[str, Any]) -> None:
    """Post-handler operations for worker listing"""
    result = ctx.get("result")
    params = ctx.get("env").params

    if not result:
        ctx["result"] = []
        return

    # Format workers as expected by the original API
    workers = []
    now = int(time.time())

    for worker in result:
        # Skip workers that haven't been seen recently
        last_seen = worker.get("last_seen", 0)
        if now - int(last_seen) > WORKER_TTL:
            continue

        # Filter by pool if specified
        if params.get("pool") and worker.get("pool") != params.get("pool"):
            continue

        # Format JSON fields
        advertises = worker.get("advertises")
        if isinstance(advertises, str):
            try:
                advertises = json.loads(advertises)
            except Exception:
                advertises = {}

        handlers = worker.get("handlers")
        if isinstance(handlers, str):
            try:
                handlers = json.loads(handlers)
            except Exception:
                handlers = []

        worker_info = {
            "id": worker.get("id"),
            **{k: v for k, v in worker.items()},
            "advertises": advertises,
            "handlers": handlers,
        }
        workers.append(worker_info)

    # Format response to match original API
    ctx["result"] = workers
