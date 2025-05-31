import time
import pytest
from peagen.queue.redis_stream_queue import RedisStreamQueue
from peagen.queue.model import Task, TaskKind, Result
from peagen.worker import OneShotWorker, WorkerConfig
from peagen.handlers.render_handler import RenderHandler
from peagen import plugin_registry


class FakeRedis:
    def __init__(self):
        self.streams = {"peagen.tasks": [], "peagen.results": [], "peagen.dead": []}
        self.groups = {}

    def xgroup_create(self, stream, groupname, id="0-0", mkstream=True):
        self.groups[groupname] = []

    def expire(self, *a, **k):
        pass

    def xadd(self, stream, fields, maxlen=None):
        msg_id = str(len(self.streams[stream]) + 1)
        self.streams[stream].append((msg_id, fields))
        return msg_id

    def xreadgroup(self, groupname, consumername, streams, count=1, block=0):
        items = self.streams["peagen.tasks"]
        if not items:
            return None
        msg = items.pop(0)
        self.groups[groupname].append(msg)
        return [("peagen.tasks", [msg])]

    def xack(self, stream, group, msg_id):
        self.groups[group] = [m for m in self.groups[group] if m[0] != msg_id]

    def xdel(self, stream, msg_id):
        pass

    def xadd_result(self, stream, fields):
        self.streams[stream].append((str(len(self.streams[stream])+1), fields))

    def xread(self, streams, block=0, count=1):
        stream = list(streams.keys())[0]
        last = streams[stream]
        data = [m for m in self.streams[stream] if m[0] > last]
        if data:
            return [(stream, [data[0]])]
        time.sleep(0.01)
        return None

    def xautoclaim(self, stream, group, consumer, min_idle_time, start_id="0-0", count=1):
        pel = self.groups.get(group, [])
        if not pel:
            return ("0-0", [])
        msg = pel.pop(0)
        return (msg[0], [msg])


@pytest.mark.integration_redis
def test_worker_flow_with_fake_redis(monkeypatch, tmp_path):
    fake = FakeRedis()
    monkeypatch.setattr("redis.Redis.from_url", lambda *a, **k: fake)
    plugin_registry.registry.setdefault("task_handlers", {})["render"] = RenderHandler

    q = RedisStreamQueue("redis://test")
    dest = tmp_path / "out.txt"
    q.enqueue(Task(TaskKind.RENDER, "r1", {"template": "hi", "vars": {}, "dest": str(dest)}, requires={"cpu"}))

    cfg = WorkerConfig(queue_url="redis://test", caps={"cpu"})
    worker = OneShotWorker(cfg)
    reason = worker.run()
    assert reason == "ok"
    res = q.wait_for_result("r1", 1)
    assert res is not None and res.status == "ok"
    assert dest.read_text() == "hi"
    assert not fake.streams["peagen.tasks"]
