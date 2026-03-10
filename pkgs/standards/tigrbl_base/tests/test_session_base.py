import asyncio

import pytest

from tigrbl_base._base._session_base import TigrblSessionBase
from tigrbl_core._spec.session_spec import SessionSpec


class StubSession(TigrblSessionBase):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []
        self.items: list[object] = []

    async def _tx_begin_impl(self) -> None:
        self.events.append("begin")

    async def _tx_commit_impl(self) -> None:
        self.events.append("commit")

    async def _tx_rollback_impl(self) -> None:
        self.events.append("rollback")

    def _add_impl(self, obj):
        self.items.append(obj)

    async def _delete_impl(self, obj):
        self.items.remove(obj)

    async def _flush_impl(self) -> None:
        self.events.append("flush")

    async def _refresh_impl(self, obj) -> None:
        self.events.append(f"refresh:{obj}")

    async def _get_impl(self, model: type, ident):
        return (model, ident)

    async def _execute_impl(self, stmt):
        return {"stmt": stmt}

    async def _close_impl(self) -> None:
        self.events.append("close")


@pytest.mark.asyncio
async def test_session_base_core_behaviors() -> None:
    session = StubSession()
    session.apply_spec(SessionSpec(read_only=False))

    await session.begin()
    assert session.in_transaction()

    session.add("x")
    await session.flush()
    await session.refresh("x")
    assert await session.get(str, 1) == (str, 1)
    assert await session.execute("SELECT 1") == {"stmt": "SELECT 1"}

    await session.commit()
    assert not session.in_transaction()
    await session.close()
    assert session.events == ["begin", "flush", "refresh:x", "flush", "commit", "close"]


@pytest.mark.asyncio
async def test_session_base_read_only_guards() -> None:
    session = StubSession()
    session.apply_spec(SessionSpec(read_only=True))

    with pytest.raises(RuntimeError, match="read-only"):
        session.add("x")

    session._dirty = True
    with pytest.raises(RuntimeError, match="read-only session"):
        await session.commit()


@pytest.mark.asyncio
async def test_session_base_run_sync_awaitable() -> None:
    session = StubSession()

    async def async_fn(_):
        await asyncio.sleep(0)
        return 42

    assert await session.run_sync(lambda _: 1) == 1
    assert await session.run_sync(async_fn) == 42
