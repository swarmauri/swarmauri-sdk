import pytest
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind
from peagen.worker import InlineWorker
from peagen.handlers.render_handler import RenderHandler
from peagen import plugin_registry


@pytest.mark.integration_stub
def test_render_task_via_inline_worker(tmp_path):
    plugin_registry.registry.setdefault("task_handlers", {})["render"] = RenderHandler
    q = StubQueue()
    dest = tmp_path / "out.txt"
    task = Task(TaskKind.RENDER, "1", {"template": "hi", "vars": {}, "dest": str(dest)}, requires={"cpu"})
    q.enqueue(task)
    worker = InlineWorker(q, caps={"cpu"})
    worker.run_once()
    assert dest.read_text() == "hi"
    assert q.pending_count() == 0
