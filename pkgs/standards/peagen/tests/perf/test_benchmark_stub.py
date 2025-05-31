import pytest
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind
from peagen.worker import InlineWorker
from peagen.handlers.render_handler import RenderHandler
from peagen import plugin_registry


@pytest.mark.perf
def test_run_once_benchmark(tmp_path, benchmark):
    plugin_registry.registry.setdefault("task_handlers", {})["render"] = RenderHandler
    q = StubQueue()
    dest = tmp_path / "out.txt"
    q.enqueue(Task(TaskKind.RENDER, "b1", {"template": "hi", "vars": {}, "dest": str(dest)}, requires={"cpu"}))
    worker = InlineWorker(q, caps={"cpu"})

    def run():
        worker.run_once()

    benchmark(run)
    assert dest.exists()
