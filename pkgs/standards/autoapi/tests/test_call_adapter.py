import asyncio
import inspect

import pytest

from autoapi.v2.impl.call_adapter import OpCall, in_event_loop


async def add_one(x: int) -> int:
    return x + 1


async def boom() -> None:
    raise ValueError("boom")


def test_in_event_loop_sync() -> None:
    assert not in_event_loop()


@pytest.mark.asyncio
async def test_in_event_loop_async() -> None:
    assert in_event_loop()


def test_sync_call() -> None:
    op = OpCall(add_one)
    assert op(1) == 2


@pytest.mark.asyncio
async def test_async_call() -> None:
    op = OpCall(add_one)
    coro = op(1)
    assert inspect.iscoroutine(coro)
    assert await coro == 2


def test_a_returns_coroutine() -> None:
    op = OpCall(add_one)
    assert asyncio.run(op.a(1)) == 2


def test_exception_sync() -> None:
    op = OpCall(boom)
    with pytest.raises(ValueError):
        op()


@pytest.mark.asyncio
async def test_exception_async() -> None:
    op = OpCall(boom)
    with pytest.raises(ValueError):
        await op()
