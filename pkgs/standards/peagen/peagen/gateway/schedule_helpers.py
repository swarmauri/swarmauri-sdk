
async def _remove_worker(workerId: str) -> None:
    """Expire the worker's registry entry immediately."""
    await queue.expire(WORKER_KEY.format(workerId), 0)
    await _publish_event("worker.update", {"id": workerId, "removed": True})


async def _live_workers_by_pool(pool: str) -> list[dict]:
    keys = await queue.keys("worker:*")
    workers = []
    now = int(time.time())
    for k in keys:
        w = await queue.hgetall(k)
        if not w:  # TTL expired or never registered
            continue
        if now - int(w["last_seen"]) > WORKER_TTL:
            continue  # stale
        if w["pool"] == pool:
            wid = k.split(":", 1)[1]
            workers.append({"id": wid, **w})
    return workers

# ──────────────────── Worker Compat ────────────────

def _pick_worker(workers: list[dict], action: str | None) -> dict | None:
    """Return the first worker that advertises *action*."""
    if action is None:
        return None
    for w in workers:
        raw = w.get("handlers", [])
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:  # noqa: BLE001
                raw = []
        if action in raw:
            return w
    return None