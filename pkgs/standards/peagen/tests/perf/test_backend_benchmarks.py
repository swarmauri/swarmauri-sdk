import asyncio
import uuid
import pytest

from peagen.models.task.task_run import TaskRun
from peagen.models.task.status import Status
from peagen.plugins.result_backends.localfs_backend import LocalFsResultBackend
from peagen.plugins.result_backends.postgres_backend import PostgresResultBackend
from peagen.plugins.result_backends.in_memory_backend import InMemoryResultBackend


@pytest.fixture()
def dummy_task_run(tmp_path):
    return TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.success,
        payload={},
        result=None,
    )


@pytest.mark.perf
def test_in_memory_backend_benchmark(benchmark, dummy_task_run):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    backend = InMemoryResultBackend()

    def run():
        loop.run_until_complete(backend.store(dummy_task_run))

    benchmark(run)
    loop.close()
    asyncio.set_event_loop(None)


@pytest.mark.perf
def test_localfs_backend_benchmark(benchmark, dummy_task_run, tmp_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    backend = LocalFsResultBackend(root_dir=tmp_path)

    def run():
        loop.run_until_complete(backend.store(dummy_task_run))

    benchmark(run)
    loop.close()
    asyncio.set_event_loop(None)


@pytest.mark.perf
def test_postgres_backend_benchmark(monkeypatch, benchmark, dummy_task_run):
    calls = {}

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def commit(self):
            calls["committed"] = True

    async def fake_upsert(session, task_run):
        calls["task"] = task_run
        calls["session"] = session

    monkeypatch.setattr(
        "peagen.plugins.result_backends.postgres_backend.Session",
        lambda: DummySession(),
    )
    monkeypatch.setattr(
        "peagen.plugins.result_backends.postgres_backend.upsert_task", fake_upsert
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    backend = PostgresResultBackend(dsn="postgres://x")

    def run():
        loop.run_until_complete(backend.store(dummy_task_run))

    benchmark(run)
    loop.close()
    asyncio.set_event_loop(None)
