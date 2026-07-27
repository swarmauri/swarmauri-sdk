import asyncio
import threading

import pytest

from swarmauri_base.tools import ToolExecutionPolicy, ToolExecutorBase


def test_required_approval_denies_without_invoking_tool() -> None:
    invoked = False

    def tool() -> None:
        nonlocal invoked
        invoked = True

    result = ToolExecutorBase(
        policy=ToolExecutionPolicy(require_approval=True)
    ).execute(tool, {}, call_id="denied")

    assert result.status == "denied"
    assert not invoked


@pytest.mark.asyncio
async def test_async_approval_precedes_invocation() -> None:
    invoked = False

    async def approve(request) -> bool:
        assert request.call_id == "approved"
        return True

    async def tool() -> str:
        nonlocal invoked
        invoked = True
        return "ok"

    executor = ToolExecutorBase(
        policy=ToolExecutionPolicy(
            require_approval=True,
            approval_callback=approve,
        )
    )
    result = await executor.aexecute(tool, {}, call_id="approved")

    assert result.status == "completed"
    assert result.value == "ok"
    assert invoked


@pytest.mark.asyncio
async def test_blocking_tool_timeout_wraps_thread_submission() -> None:
    release = threading.Event()

    def tool() -> None:
        release.wait(1)

    result = await ToolExecutorBase().aexecute(
        tool,
        {},
        call_id="timeout",
        timeout=0.01,
    )
    release.set()

    assert result.status == "timed_out"


@pytest.mark.asyncio
async def test_active_async_call_can_be_cancelled() -> None:
    started = asyncio.Event()

    async def tool() -> None:
        started.set()
        await asyncio.Event().wait()

    executor = ToolExecutorBase()
    execution = asyncio.create_task(
        executor.aexecute(tool, {}, call_id="cancel-me")
    )
    await started.wait()

    assert await executor.acancel("cancel-me")
    result = await execution
    assert result.status == "cancelled"
    assert result.cancelled
    assert not await executor.acancel("cancel-me")
