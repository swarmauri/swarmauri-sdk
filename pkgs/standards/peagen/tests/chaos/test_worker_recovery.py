import threading
import time
import pytest
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind
from peagen.worker import OneShotWorker, WorkerConfig
from peagen.handlers.render_handler import RenderHandler
from peagen import plugin_registry


class SlowHandler(RenderHandler):
    def handle(self, task: Task):
        time.sleep(0.2)
        return super().handle(task)


@pytest.mark.chaos
def test_worker_sigterm_recovery(monkeypatch, tmp_path):
    plugin_registry.registry.setdefault("task_handlers", {})["slow"] = SlowHandler
    q = StubQueue()
    dest = tmp_path / "out.txt"
    q.enqueue(Task(TaskKind.RENDER, "c1", {"template": "hi", "vars": {}, "dest": str(dest)}, requires={"cpu"}))
    cfg = WorkerConfig(queue_url="stub://", caps={"cpu"}, idle_exit=1)
    worker = OneShotWorker(cfg)
    monkeypatch.setattr(worker, "_select_handler", lambda t: SlowHandler())

    def run_worker():
        worker.run()

    t = threading.Thread(target=run_worker)
    t.start()
    time.sleep(0.05)
    worker._sigterm()
    t.join()

    q.requeue_orphans(idle_ms=0)
    worker2 = OneShotWorker(cfg)
    worker2.run()

    res = q.wait_for_result("c1", 1)
    assert res is not None and res.status == "ok"
    assert dest.exists()
