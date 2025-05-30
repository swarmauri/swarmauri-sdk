import multiprocessing as mp
import time

from peagen.worker import OneShotWorker, WorkerConfig
from peagen.spawner import WarmSpawner, SpawnerConfig
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind, Result
from peagen import plugin_registry


class SlowHandler:
    KIND = TaskKind.RENDER
    PROVIDES = {"cpu"}

    def __init__(self):
        pass

    def dispatch(self, task: Task) -> bool:
        return True

    def handle(self, task: Task) -> Result:
        time.sleep(5)
        return Result(task.id, "ok", {})


def _run_worker(queue_url: str) -> None:
    cfg = WorkerConfig(queue_url=queue_url, caps={"cpu"})
    OneShotWorker(cfg).run()


def test_worker_crash_requeued(monkeypatch):
    plugin_registry.registry.setdefault("task_handlers", {})["slow"] = SlowHandler

    q = StubQueue()
    q.enqueue(Task(TaskKind.RENDER, "1", {}, requires={"cpu"}))

    monkeypatch.setattr("peagen.spawner.make_queue", lambda *a, **k: q)
    monkeypatch.setattr("peagen.worker.make_queue", lambda *a, **k: q)

    processes = []

    def launch(self):
        p = mp.Process(target=_run_worker, args=("stub://",))
        p.start()
        processes.append(p)

    monkeypatch.setattr(WarmSpawner, "_launch_worker", launch)

    loops = 0
    real_sleep = time.sleep

    def sleeper(t):
        nonlocal loops
        loops += 1
        if loops == 3:
            # kill worker while task running
            if processes:
                processes[0].terminate()
        if loops > 5:
            raise SystemExit
        real_sleep(0.1)

    monkeypatch.setattr(time, "sleep", sleeper)

    sp = WarmSpawner(SpawnerConfig(queue_url="stub://", caps=["cpu"], warm_pool=1, poll_ms=100, idle_ms=200))
    with mp.get_context("spawn"):  # ensure clean start
        try:
            sp.run()
        except SystemExit:
            pass

    assert q.pending_count() == 1

