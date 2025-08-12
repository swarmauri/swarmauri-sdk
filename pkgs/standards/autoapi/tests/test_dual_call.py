import inspect


import anyio

from autoapi.v2.impl._dual_call import CallableOp, in_event_loop


def test_in_event_loop_detection():
    assert not in_event_loop()

    async def check():
        assert in_event_loop()

    anyio.run(check)


def test_callable_op_sync_and_async():
    def add(x: int) -> int:
        return x + 1

    async def add_async(x: int) -> int:
        return await anyio.to_thread.run_sync(add, x)

    op = CallableOp(add_async)
    assert op(1) == 2

    async def check():
        coro = op(1)
        assert inspect.iscoroutine(coro)
        assert await coro == 2
        assert await op.a(1) == 2

    anyio.run(check)
