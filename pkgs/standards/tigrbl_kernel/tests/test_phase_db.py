from __future__ import annotations

import pytest

from tigrbl_atoms.atoms.sys.phase_db import DbCapabilities, PhaseDb, bind_phase_db


class FakeDb:
    def __init__(self) -> None:
        self.flush_calls = 0
        self.commit_calls = 0
        self.refresh_calls = 0
        self.rollback_calls = 0

    async def flush(self) -> None:
        self.flush_calls += 1

    async def commit(self) -> None:
        self.commit_calls += 1

    async def refresh(self, instance) -> None:
        del instance
        self.refresh_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1


@pytest.mark.asyncio
async def test_phase_db_pre_handler_allows_flush_denies_commit() -> None:
    db = FakeDb()
    phase_db = PhaseDb(
        db,
        phase="PRE_HANDLER",
        caps=DbCapabilities(
            allow_flush=True,
            allow_commit=False,
            commit_requires_owned_tx=True,
            allow_refresh=False,
        ),
        owns_tx=True,
    )

    await phase_db.flush()
    assert db.flush_calls == 1

    with pytest.raises(RuntimeError, match=r"db\.commit\(\) is not allowed"):
        await phase_db.commit()


@pytest.mark.asyncio
async def test_phase_db_end_tx_requires_owned_transaction_for_commit() -> None:
    db = FakeDb()
    phase_db = PhaseDb(
        db,
        phase="END_TX",
        caps=DbCapabilities(
            allow_flush=True,
            allow_commit=True,
            commit_requires_owned_tx=True,
            allow_refresh=False,
        ),
        owns_tx=False,
    )

    with pytest.raises(RuntimeError, match=r"db\.commit\(\) is not allowed"):
        await phase_db.commit()

    assert db.commit_calls == 0


@pytest.mark.asyncio
async def test_phase_db_post_commit_allows_refresh() -> None:
    db = FakeDb()
    phase_db = PhaseDb(
        db,
        phase="POST_COMMIT",
        caps=DbCapabilities(
            allow_flush=True,
            allow_commit=False,
            commit_requires_owned_tx=True,
            allow_refresh=True,
        ),
        owns_tx=True,
    )

    await phase_db.refresh(object())
    assert db.refresh_calls == 1


def test_bind_phase_db_binds_restricted_surface_into_ctx() -> None:
    class Ctx(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__

    raw_db = FakeDb()
    ctx = Ctx()
    ctx._raw_db = raw_db
    ctx.phase = "PRE_HANDLER"
    ctx.owns_tx = True

    bind_phase_db(ctx)

    assert isinstance(ctx.db, PhaseDb)
    assert ctx.db.raw is raw_db


def test_bind_phase_db_requires_phase() -> None:
    class Ctx(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__

    ctx = Ctx()
    ctx._raw_db = FakeDb()
    with pytest.raises(RuntimeError, match="ctx.phase must be set"):
        bind_phase_db(ctx)


def test_bind_phase_db_without_db_sets_none() -> None:
    class Ctx(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__

    ctx = Ctx()
    ctx.phase = "PRE_HANDLER"
    bind_phase_db(ctx)
    assert ctx.db is None
