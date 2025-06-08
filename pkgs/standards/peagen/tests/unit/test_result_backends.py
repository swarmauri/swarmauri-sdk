import json
import uuid
import pytest

from peagen.models.task_run import TaskRun, Status
from peagen.plugins.result_backends.localfs_backend import LocalFsResultBackend
from peagen.plugins.result_backends.postgres_backend import PostgresResultBackend


@pytest.mark.unit
@pytest.mark.asyncio
async def test_localfs_backend_writes_file(tmp_path):
    backend = LocalFsResultBackend(root_dir=tmp_path)
    tr = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.success,
        payload={},
        result=None,
    )
    await backend.store(tr)
    out = tmp_path / f"{tr.id}.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["id"] == str(tr.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_postgres_backend_invokes_helpers(monkeypatch):
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

    backend = PostgresResultBackend(dsn="postgres://x")
    tr = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.success,
        payload={},
        result=None,
    )
    await backend.store(tr)

    assert calls["task"] is tr
    assert calls["committed"] is True
