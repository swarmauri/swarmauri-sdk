import asyncio
import importlib
from typing import Awaitable, Callable

import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.plugins.result_backends.in_memory_backend import InMemoryResultBackend


@pytest.fixture()
def gateway(monkeypatch):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    q = InMemoryQueue()

    class StubPM:
        def __init__(self, cfg):
            pass

        def get(self, group: str):
            if group == "queues":
                return q
            if group == "result_backends":
                return InMemoryResultBackend()
            return None

    import peagen.plugins

    monkeypatch.setattr(peagen.plugins, "PluginManager", StubPM)
    import peagen.gateway as gw

    importlib.reload(gw)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", InMemoryResultBackend())

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    task_id = asyncio.get_event_loop().run_until_complete(
        gw.task_submit(pool="p", payload={}, taskId=None)
    )["taskId"]
    yield gw, task_id
    loop.close()
    asyncio.set_event_loop(None)


METHODS: list[tuple[str, Callable[[object, str], Awaitable[None]]]] = [
    ("Pool.create", lambda gw, tid: gw.pool_create("bench")),
    ("Pool.join", lambda gw, tid: gw.pool_join("bench")),
    ("Task.submit", lambda gw, tid: gw.task_submit(pool="p", payload={}, taskId=None)),
    ("Task.cancel", lambda gw, tid: gw.task_cancel(tid)),
    ("Task.pause", lambda gw, tid: gw.task_pause(tid)),
    ("Task.resume", lambda gw, tid: gw.task_resume(tid)),
    ("Task.retry", lambda gw, tid: gw.task_retry(tid)),
    ("Task.retry_from", lambda gw, tid: gw.task_retry_from(tid)),
    ("Guard.set", lambda gw, tid: gw.guard_set("x", {})),
    ("Task.patch", lambda gw, tid: gw.task_patch(taskId=tid, changes={})),
    ("Task.get", lambda gw, tid: gw.task_get(tid)),
    ("Pool.listTasks", lambda gw, tid: gw.pool_list("p")),
    (
        "Worker.register",
        lambda gw, tid: gw.worker_register(
            "w1", pool="p", url="http://w1", advertises={}
        ),
    ),
    (
        "Worker.heartbeat",
        lambda gw, tid: gw.worker_heartbeat(
            "w1", metrics={}, pool="p", url="http://w1"
        ),
    ),
    ("Worker.list", lambda gw, tid: gw.worker_list()),
    (
        "Work.finished",
        lambda gw, tid: gw.work_finished(tid, status="success", result=None),
    ),
]


@pytest.mark.perf
@pytest.mark.parametrize("_name,call", METHODS)
def test_gateway_methods_benchmark(benchmark, gateway, _name, call):
    gw, tid = gateway

    async def runner() -> None:
        await call(gw, tid)

    benchmark(lambda: asyncio.run(runner()))
