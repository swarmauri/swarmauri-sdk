import pytest
from swarmauri_agent_runner import AgentRunner, AgentRunnerExecutionDriver
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_core.executions import ExecutionSnapshot

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_driver_yields_between_model_tool_roundtrips(tmp_path):
    calls = []

    def model(messages, tools):
        calls.append(messages)
        return {"role": "assistant", "content": "done"}

    runner = AgentRunner(model, SqliteRunStore(path=tmp_path / "runs.db"))
    initialized = runner.initialize("hello")
    assert calls == []
    driver = AgentRunnerExecutionDriver(runner=runner)
    result = await driver.step(
        ExecutionSnapshot(
            "execution",
            "task",
            "agent",
            state={"prompt": "hello", "run_id": initialized.run_id},
        )
    )
    assert result.completed and result.result == "done"
    assert len(calls) == 1
