from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind


def test_requeue_orphan():
    q = StubQueue()
    task = Task(TaskKind.RENDER, "1", {}, requires=set())
    q.enqueue(task)
    claimed = q.pop(block=False)
    assert claimed is not None
    moved = q.requeue_orphans(idle_ms=0, max_batch=10)
    assert moved == 1
    assert q.pop(block=False).id == "1"
