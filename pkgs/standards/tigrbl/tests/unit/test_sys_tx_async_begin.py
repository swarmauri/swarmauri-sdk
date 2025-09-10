import asyncio
from types import SimpleNamespace

import pytest

from tigrbl.runtime import system


class _AsyncBeginSyncCommitDB:
    def __init__(self) -> None:
        self.started = False
        self.committed = False

    async def begin(self) -> None:  # pragma: no cover - executed via await
        self.started = True

    def commit(self) -> None:  # pragma: no cover - executed if tx began
        if self.started:
            self.committed = True

    def in_transaction(self) -> bool:
        return self.started


@pytest.mark.asyncio
async def test_sys_tx_handles_async_begin_sync_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = _AsyncBeginSyncCommitDB()
    ctx = SimpleNamespace(db=db, temp={})
    loop = asyncio.get_running_loop()

    def begin(c: SimpleNamespace) -> None:
        loop.create_task(c.db.begin())

    def commit(c: SimpleNamespace) -> None:
        c.db.commit()

    monkeypatch.setattr(system.INSTALLED, "begin", begin)
    monkeypatch.setattr(system.INSTALLED, "commit", commit)

    system._sys_tx_begin(None, ctx)
    await asyncio.sleep(0)
    await system._sys_tx_commit(None, ctx)
    assert db.started and db.committed
