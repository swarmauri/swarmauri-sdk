from peagen.worker import OneShotWorker, WorkerConfig, ITaskHandler
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


def test_worker_runs_single_task(monkeypatch):
    plugin_registry.registry.setdefault("task_handlers", {})["echo"] = EchoHandler
    q = StubQueue()
    task = Task(TaskKind.RENDER, "1", {"x": 1}, requires={"cpu"})
    q.enqueue(task)

    monkeypatch.setattr("peagen.worker.make_queue", lambda *a, **k: q)
    cfg = WorkerConfig(queue_url="stub://", caps={"cpu"}, idle_exit=1)
    worker = OneShotWorker(cfg)
    reason = worker.run()
    assert reason == "ok"
    res = q.wait_for_result("1", 1)
    assert res is not None
    assert res.status == "ok"
