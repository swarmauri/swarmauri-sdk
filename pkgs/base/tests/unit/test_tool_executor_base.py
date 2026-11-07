import asyncio

import pytest

from swarmauri_base.tools.ToolExecutorBase import ToolExecutorBase


def test_sync_tool_execution_preserves_call_correlation() -> None:
    result = ToolExecutorBase().execute(
        lambda value: value + 1, {"value": 1}, call_id="call-1"
    )

    assert result.call_id == "call-1"
    assert result.value == 2


@pytest.mark.asyncio
async def test_async_executor_supports_async_and_blocking_tools() -> None:
    async def async_tool(value: int) -> int:
        await asyncio.sleep(0)
        return value + 1

    executor = ToolExecutorBase()
    async_result = await executor.aexecute(
        async_tool, {"value": 1}, call_id="async"
    )
    sync_result = await executor.aexecute(
        lambda value: value + 2, {"value": 1}
    )

    assert async_result.value == 2
    assert sync_result.value == 3
