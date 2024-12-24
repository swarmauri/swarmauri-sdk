from typing import Any
from pydantic import BaseModel
import pytest
import asyncio
from swarmauri.swarms.base.SwarmBase import SwarmStatus
from swarmauri.swarms.concrete.Swarm import Swarm


class MockAgent(BaseModel):
    async def process(self, task: Any, **kwargs) -> str:
        if task == "fail":
            raise Exception("Task failed")
        return f"Processed {task}"

@pytest.fixture
def swarm():
    return Swarm(agent_class=MockAgent, num_agents=3, agent_timeout=0.5, max_retries=2)

@pytest.mark.unit
def test_ubc_resource(swarm):
    assert swarm.resource == "Swarm"


@pytest.mark.unit
def test_ubc_type(swarm):
    assert swarm.type == "Swarm"


@pytest.mark.unit
def test_serialization(swarm):
    assert swarm.id == Swarm.model_validate_json(swarm.model_dump_json()).id


@pytest.mark.asyncio
async def test_swarm_initialization(swarm):
    assert len(swarm.agents) == 3
    assert swarm.queue_size == 0
    assert all(s == SwarmStatus.IDLE for s in swarm.get_swarm_status().values())


@pytest.mark.asyncio
async def test_single_task_execution(swarm):
    results = await swarm.exec("task1")
    assert len(results) == 1
    assert results[0]["status"] == SwarmStatus.COMPLETED
    assert results[0]["result"] == "Processed task1"
    assert "agent_id" in results[0]


@pytest.mark.asyncio
async def test_multiple_tasks_execution(swarm):
    tasks = ["task1", "task2", "task3"]
    results = await swarm.exec(tasks)
    assert len(results) == 3
    assert all(r["status"] == SwarmStatus.COMPLETED for r in results)
    assert all("Processed" in r["result"] for r in results)


@pytest.mark.asyncio
async def test_failed_task_handling(swarm):
    results = await swarm.exec("fail")
    assert len(results) == 1
    assert results[0]["status"] == SwarmStatus.FAILED
    assert "error" in results[0]


@pytest.mark.asyncio(loop_scope="session")
async def test_swarm_status_changes(swarm):
    # Create tasks
    tasks = ["task1"] * 3

    # Start execution
    task_future = asyncio.create_task(swarm.exec(tasks))

    # Wait briefly for tasks to start
    await asyncio.sleep(0.1)

    # Check intermediate status
    status = swarm.get_swarm_status()
    assert any(
        s in [SwarmStatus.WORKING, SwarmStatus.COMPLETED] for s in status.values()
    )

    # Wait for completion with timeout
    try:
        results = await asyncio.wait_for(task_future, timeout=2.0)
        assert len(results) == len(tasks)
        assert all(r["status"] == SwarmStatus.COMPLETED for r in results)
    except asyncio.TimeoutError:
        task_future.cancel()
        raise
