import uuid
import pytest

from peagen.plugins.selectors import (
    ResultBackendSelector,
    BootstrapSelector,
    InputSelector,
)
from peagen.plugins.result_backends.in_memory_backend import InMemoryResultBackend
from peagen.orm.task.task_run import TaskRun
from peagen.orm.status import Status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_result_backend_selector_picks_leader_and_running_candidates():
    backend = InMemoryResultBackend()
    tr1 = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.running,
        payload={},
        result=None,
    )
    tr2 = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.success,
        payload={},
        result={"score": 1},
    )
    tr3 = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.running,
        payload={},
        result=None,
    )
    await backend.store(tr1)
    await backend.store(tr2)
    await backend.store(tr3)

    selector = ResultBackendSelector(backend, num_candidates=2)
    result = await selector.select()

    assert result["leader"]["id"] == str(tr2.id)
    ids = {c["id"] for c in result["candidates"]}
    assert ids == {str(tr1.id), str(tr3.id)}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_bootstrap_selector_switches_after_first_call():
    backend = InMemoryResultBackend()
    tr = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.running,
        payload={},
        result=None,
    )
    await backend.store(tr)
    selector = BootstrapSelector(backend, bootstrap=[{"id": "boot"}], num_candidates=1)

    first = await selector.select()
    assert first == {"leader": None, "candidates": [{"id": "boot"}]}

    second = await selector.select()
    assert second["candidates"][0]["id"] == str(tr.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_input_selector_uses_initial_candidate_once():
    backend = InMemoryResultBackend()
    tr = TaskRun(
        id=uuid.uuid4(),
        pool="p",
        task_type="t",
        status=Status.running,
        payload={},
        result=None,
    )
    await backend.store(tr)

    selector = InputSelector(backend, {"id": "user"}, num_candidates=1)

    first = await selector.select()
    assert first == {"leader": None, "candidates": [{"id": "user"}]}

    second = await selector.select()
    assert second["candidates"][0]["id"] == str(tr.id)
