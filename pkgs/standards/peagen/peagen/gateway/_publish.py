
# ──────────────────────   Publish Event  ─────────────────────────
# ------------------------------------------------------------------
# 1. publish an event (unchanged — shown for completeness)
# ------------------------------------------------------------------
async def _publish_event(event_type: str, data: dict) -> None:
    event = {
        "type": event_type,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": data,
    }
    await queue.publish(PUBSUB_TOPIC, json.dumps(event, default=str))


# ------------------------------------------------------------------
# 3. broadcast a single task update
# ------------------------------------------------------------------
async def _publish_task(task: TaskBlob) -> None:
    data = dict(task)  # shallow copy
    if "duration" in task and task["duration"] is not None:
        data["duration"] = task["duration"]
    await _publish_event("task.update", data)


async def _publish_queue_length(pool: str) -> None:
    qlen = len(await queue.lrange(f"{READY_QUEUE}:{pool}", 0, -1))
    await _publish_event("queue.update", {"pool": pool, "length": qlen})