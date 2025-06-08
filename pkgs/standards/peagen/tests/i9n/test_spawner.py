import pytest

from peagen.spawner import WarmSpawner, SpawnerConfig
from peagen.worker import OneShotWorker
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind, Result
from peagen import plugin_registry


class EchoHandler:
    KIND = TaskKind.RENDER
    PROVIDES = {"cpu"}

    def dispatch(self, task: Task) -> bool:
        return True

    def handle(self, task: Task) -> Result:
        return Result(task_id=task.id, status="ok", data=task.payload)


def test_spawner_launch(monkeypatch):
    plugin_registry.registry.setdefault("task_handlers", {})["echo"] = EchoHandler
    q = StubQueue()
    q.enqueue(Task(TaskKind.RENDER, "1", {}, requires={"cpu"}))

    monkeypatch.setattr("peagen.spawner.make_queue", lambda *a, **k: q)
    monkeypatch.setattr("peagen.worker.make_queue", lambda *a, **k: q)

    launched = []
    monkeypatch.setattr(WarmSpawner, "_launch_worker", lambda self: launched.append(1))
    monkeypatch.setattr("time.sleep", lambda x: (_ for _ in ()).throw(SystemExit))

    cfg = SpawnerConfig(queue_url="stub://", caps=["cpu"], warm_pool=1, poll_ms=1)
    sp = WarmSpawner(cfg)
    with pytest.raises(SystemExit):
        sp.run()
    assert launched
