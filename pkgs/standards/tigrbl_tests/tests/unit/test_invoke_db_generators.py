import pytest

from tigrbl.runtime.executor.invoke import _invoke


class _FakeSession:
    def __init__(self) -> None:
        self.commit = object()

    def in_transaction(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_invoke_consumes_sync_db_generator() -> None:
    session = _FakeSession()
    closed = False

    def get_db():
        nonlocal closed
        try:
            yield session
        finally:
            closed = True

    phases = {
        "HANDLER": [
            lambda ctx: ctx.update(
                saw_commit=hasattr(ctx.db, "commit"), result={"ok": True}
            )
        ],
    }

    result = await _invoke(
        request=None,
        db=get_db(),
        phases=phases,
        ctx={"temp": {}},
    )

    assert result == {"ok": True}
    assert session.commit is not None
    assert closed is True


@pytest.mark.asyncio
async def test_invoke_consumes_async_db_generator() -> None:
    session = _FakeSession()
    closed = False

    async def get_db():
        nonlocal closed
        try:
            yield session
        finally:
            closed = True

    phases = {
        "HANDLER": [
            lambda ctx: ctx.update(
                saw_commit=hasattr(ctx.db, "commit"), result={"ok": True}
            )
        ],
    }

    result = await _invoke(
        request=None,
        db=get_db(),
        phases=phases,
        ctx={"temp": {}},
    )

    assert result == {"ok": True}
    assert session.commit is not None
    assert closed is True
