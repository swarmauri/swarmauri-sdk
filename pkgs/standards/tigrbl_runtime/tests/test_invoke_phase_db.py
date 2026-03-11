from __future__ import annotations

import pytest

from tigrbl_atoms.atoms.sys.phase_db import bind_phase_db
from tigrbl_runtime.executors.invoke import _invoke


class FakeDb:
    def __init__(self) -> None:
        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self._in_tx = False

    def in_transaction(self) -> bool:
        return self._in_tx

    async def begin(self) -> None:
        self._in_tx = True

    async def flush(self) -> None:
        self.flush_calls += 1

    async def commit(self) -> None:
        self.commit_calls += 1
        self._in_tx = False

    async def rollback(self) -> None:
        self.rollback_calls += 1
        self._in_tx = False


@pytest.mark.asyncio
async def test_pre_handler_commit_is_denied_via_phase_db() -> None:
    db = FakeDb()

    async def start_tx(ctx):
        await db.begin()

    async def pre_handler(ctx):
        await ctx.db.commit()

    phases = {
        "START_TX": [bind_phase_db, start_tx],
        "PRE_HANDLER": [bind_phase_db, pre_handler],
    }

    with pytest.raises(Exception, match=r"db\.commit\(\) is not allowed"):
        await _invoke(request=None, db=db, phases=phases, ctx={})

    assert db.commit_calls == 0
    assert db.rollback_calls == 1


@pytest.mark.asyncio
async def test_end_tx_commit_is_allowed_when_runtime_owns_transaction() -> None:
    db = FakeDb()

    async def start_tx(ctx):
        await db.begin()

    async def end_tx(ctx):
        await ctx.db.commit()

    phases = {
        "START_TX": [bind_phase_db, start_tx],
        "END_TX": [bind_phase_db, end_tx],
    }

    result = await _invoke(request=None, db=db, phases=phases, ctx={})

    assert result is None
    assert db.commit_calls == 1
    assert db.rollback_calls == 0


@pytest.mark.asyncio
async def test_pre_commit_flush_is_denied_via_phase_db() -> None:
    db = FakeDb()

    async def start_tx(ctx):
        await db.begin()

    async def pre_commit(ctx):
        await ctx.db.flush()

    phases = {
        "START_TX": [bind_phase_db, start_tx],
        "PRE_COMMIT": [bind_phase_db, pre_commit],
    }

    with pytest.raises(Exception, match=r"db\.flush\(\) is not allowed"):
        await _invoke(request=None, db=db, phases=phases, ctx={})

    assert db.flush_calls == 0
    assert db.rollback_calls == 1


@pytest.mark.asyncio
async def test_invoke_without_db_allows_phase_db_binding_no_crash() -> None:
    async def handler(ctx):
        ctx.result = {"ok": True}

    result = await _invoke(
        request=None,
        db=None,
        phases={"HANDLER": [bind_phase_db, handler]},
        ctx={},
    )

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_response_result_sync_remains_after_phase_db_refactor() -> None:
    async def handler(ctx):
        ctx.response = {"result": "initial"}
        ctx.result = "updated"

    result = await _invoke(
        request=None,
        db=None,
        phases={"HANDLER": [bind_phase_db, handler]},
        ctx={},
    )

    assert result == "updated"
