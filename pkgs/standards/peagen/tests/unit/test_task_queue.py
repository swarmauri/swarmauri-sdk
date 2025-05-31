import time
from peagen.queue.stub_queue import StubQueue
from peagen.queue.redis_stream_queue import RedisStreamQueue
from peagen.queue.model import Task, TaskKind, Result


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


def test_stubqueue_flow():
    q = StubQueue()
    task = Task(TaskKind.MUTATE, "1", {})
    q.enqueue(task)
    got = q.pop(block=False)
    assert got.id == "1"
    res = Result(task_id="1", status="ok", data={})
    q.ack("1")
    q.push_result(res)
    assert q.wait_for_result("1", 1) == res


def test_stubqueue_requeue():
    q = StubQueue()
    task = Task(TaskKind.MUTATE, "1", {})
    q.enqueue(task)
    _ = q.pop(block=False)
    time.sleep(0.01)
    moved = q.requeue_orphans(idle_ms=0, max_batch=10)
    assert moved == 1
    assert q.pop(block=False).id == "1"


def test_redisqueue_basic(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("redis.Redis.from_url", lambda *a, **k: fake)
    q = RedisStreamQueue("redis://test")
    task = Task(TaskKind.RENDER, "t1", {})
    q.enqueue(task)
    got = q.pop(block=False)
    assert got.id == "t1"
    q.ack("t1")
    result = Result(task_id="t1", status="ok", data={})
    q.push_result(result)
    assert q.wait_for_result("t1", 1).task_id == "t1"


def test_list_pending_stubqueue():
    q = StubQueue()
    q.enqueue(Task(TaskKind.RENDER, "t1", {}))
    q.enqueue(Task(TaskKind.MUTATE, "t2", {}))
    tasks = list(q.list_pending())
    assert [t.id for t in tasks] == ["t1", "t2"]
    _ = q.pop(block=False)
    ids = [t.id for t in q.list_pending()]
    assert set(ids) == {"t1", "t2"}


def test_list_pending_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("redis.Redis.from_url", lambda *a, **k: fake)
    q = RedisStreamQueue("redis://test")
    q.enqueue(Task(TaskKind.RENDER, "a", {}))
    q.enqueue(Task(TaskKind.MUTATE, "b", {}))
    ids = [t.id for t in q.list_pending()]
    assert ids == ["a", "b"]
