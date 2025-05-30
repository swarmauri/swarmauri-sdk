import os
import uuid
from collections import deque
from dataclasses import dataclass, field

import pytest


@dataclass
class RenderTask:
    output_dir: str
    file_name: str = "hello.txt"
    id: str = field(init=False)

    def __post_init__(self):
        self.id = str(uuid.uuid4())

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)
        with open(os.path.join(self.output_dir, self.file_name), "w", encoding="utf-8") as f:
            f.write("hello")


class StubQueue:
    def __init__(self):
        self._todo = deque()
        self._inflight = {}

    def enqueue(self, task):
        self._todo.append(task)

    def pop(self, block=True, timeout=1):
        if self._todo:
            task = self._todo.popleft()
            self._inflight[task.id] = task
            return task
        return None

    def ack(self, task_id):
        self._inflight.pop(task_id, None)

    @property
    def queue_pending_total(self):
        return len(self._todo) + len(self._inflight)


class InlineWorker:
    def __init__(self, queue: StubQueue):
        self.queue = queue

    def run_once(self):
        task = self.queue.pop(block=False)
        if not task:
            return
        task.run()
        self.queue.ack(task.id)


@pytest.mark.integration_stub
def test_stub_queue_worker(tmp_path):
    queue = StubQueue()
    worker = InlineWorker(queue)

    task = RenderTask(output_dir=str(tmp_path))
    queue.enqueue(task)

    worker.run_once()

    assert (tmp_path / task.file_name).exists()
    assert queue.queue_pending_total == 0

