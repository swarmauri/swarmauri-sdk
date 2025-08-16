import pytest
from autoapi.v3.bindings import hooks


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
async def test_start_tx_handles_async_begin_sync_commit() -> None:
    db = _AsyncBeginSyncCommitDB()
    ctx = {"db": db}
    await hooks._default_start_tx()(ctx)
    await hooks._default_end_tx()(ctx)
    assert db.started and db.committed
