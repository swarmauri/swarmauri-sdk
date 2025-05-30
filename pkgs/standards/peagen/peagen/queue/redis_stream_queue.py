from __future__ import annotations

import json
import os
import time
import uuid
from typing import Dict

import redis

from .base import TaskQueue
from .model import Task, Result


class RedisStreamQueue(TaskQueue):
    STREAM_TASKS = "peagen.tasks"
    STREAM_RESULTS = "peagen.results"
    STREAM_DEAD = "peagen.dead"

    def __init__(self, url: str, *, group: str = "peagen", idle_ms: int = 60000, max_retry: int = 3) -> None:
        self._r = redis.Redis.from_url(url, decode_responses=True)
        self.group = group
        self.consumer = os.environ.get("HOSTNAME", "consumer-" + uuid.uuid4().hex[:6])
        self.idle_ms = idle_ms
        self.max_retry = max_retry
        self._msg_map: Dict[str, str] = {}
        self._ensure_streams()

    def _ensure_streams(self) -> None:
        try:
            self._r.xgroup_create(self.STREAM_TASKS, self.group, id="0-0", mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        self._r.expire(self.STREAM_TASKS, 14 * 24 * 3600)
        self._r.expire(self.STREAM_RESULTS, 14 * 24 * 3600)
        self._r.expire(self.STREAM_DEAD, 30 * 24 * 3600)

    # ------------------------------------------------------------------ producer
    def enqueue(self, task: Task) -> None:
        data = json.dumps(task.to_dict())
        msg_id = self._r.xadd(self.STREAM_TASKS, {"data": data}, maxlen=10_000_000)
        self._msg_map[task.id] = msg_id

    # ------------------------------------------------------------------ consumer
    def pop(self, block: bool = True, timeout: int = 1) -> Task | None:
        res = self._r.xreadgroup(
            self.group,
            self.consumer,
            {self.STREAM_TASKS: ">"},
            count=1,
            block=timeout * 1000 if block else 0,
        )
        if not res:
            return None
        _, messages = res[0]
        msg_id, fields = messages[0]
        data = json.loads(fields["data"])
        task = Task(**data)
        self._msg_map[task.id] = msg_id
        return task

    def ack(self, task_id: str) -> None:
        msg_id = self._msg_map.pop(task_id, None)
        if msg_id:
            self._r.xack(self.STREAM_TASKS, self.group, msg_id)
            self._r.xdel(self.STREAM_TASKS, msg_id)

    # ------------------------------------------------------------------ admin
    def push_result(self, result: Result) -> None:
        data = json.dumps(result.to_dict())
        self._r.xadd(self.STREAM_RESULTS, {"data": data}, maxlen=10_000_000)

    def wait_for_result(self, task_id: str, timeout: int) -> Result | None:
        end = time.time() + timeout
        last_id = "0-0"
        while time.time() < end:
            res = self._r.xread({self.STREAM_RESULTS: last_id}, block=1000, count=1)
            if not res:
                continue
            _, messages = res[0]
            msg_id, fields = messages[0]
            last_id = msg_id
            data = json.loads(fields["data"])
            if data["task_id"] == task_id:
                return Result(**data)
        return None

    def requeue_orphans(self, idle_ms: int = 60000, max_batch: int = 50) -> int:
        moved = 0
        start = "0-0"
        while moved < max_batch:
            msg_id, msgs = self._r.xautoclaim(
                self.STREAM_TASKS,
                self.group,
                self.consumer,
                min_idle_time=idle_ms,
                start_id=start,
                count=max_batch - moved,
            )
            if not msgs:
                break
            for mid, fields in msgs:
                data = json.loads(fields["data"])
                task = Task(**data)
                task.attempts += 1
                if task.attempts > self.max_retry:
                    self._r.xadd(self.STREAM_DEAD, {"data": json.dumps(task.to_dict())})
                    self._r.xack(self.STREAM_TASKS, self.group, mid)
                    self._r.xdel(self.STREAM_TASKS, mid)
                else:
                    self._r.xadd(self.STREAM_TASKS, {"data": json.dumps(task.to_dict())})
                    self._r.xack(self.STREAM_TASKS, self.group, mid)
                    self._r.xdel(self.STREAM_TASKS, mid)
                moved += 1
            start = msg_id
            if msg_id == "0-0":
                break
        return moved
