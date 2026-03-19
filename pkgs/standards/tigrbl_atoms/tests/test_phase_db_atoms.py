from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.sys import _db
from tigrbl_atoms.atoms.sys import phase_db


def test_phase_db_capabilities_known_phase_values() -> None:
    caps = phase_db.phase_db_capabilities("END_TX")

    assert isinstance(caps, phase_db.DbCapabilities)
    assert caps.allow_flush is True
    assert caps.allow_commit is True
    assert caps.commit_requires_owned_tx is True
    assert caps.allow_refresh is False


def test_phase_db_capabilities_unknown_phase_raises_runtime_error() -> None:
    with pytest.raises(RuntimeError, match="Unknown phase"):
        phase_db.phase_db_capabilities("NOT_A_REAL_PHASE")


def test_bind_phase_db_requires_phase_when_raw_db_present() -> None:
    ctx = SimpleNamespace(_raw_db=object(), phase=None, owns_tx=False)

    with pytest.raises(RuntimeError, match="ctx.phase must be set"):
        phase_db.bind_phase_db(ctx)


def test_bind_phase_db_sets_none_db_without_raw_db() -> None:
    ctx = SimpleNamespace()

    out = phase_db.bind_phase_db(ctx)

    assert out is ctx
    assert ctx.db is None


def test_bind_phase_db_wraps_db_with_phase_caps_and_tx_ownership() -> None:
    raw_db = object()
    ctx = SimpleNamespace(_raw_db=raw_db, phase="POST_COMMIT", owns_tx=True)

    out = phase_db.bind_phase_db(ctx)

    assert out is ctx
    assert isinstance(ctx.db, phase_db.PhaseDb)
    assert ctx.db.raw is raw_db


def test_phase_db_run_uses_bind_phase_db_contract() -> None:
    raw_db = object()
    ctx = SimpleNamespace(_raw_db=raw_db, phase="PRE_HANDLER", owns_tx=False)

    out = phase_db.run(ctx)

    assert out is ctx
    assert isinstance(ctx.db, phase_db.PhaseDb)
    assert ctx.db.raw is raw_db


def test_phase_db_enforces_flush_commit_and_refresh_rules() -> None:
    calls: list[str] = []

    class Db:
        def flush(self) -> None:
            calls.append("flush")

        def commit(self) -> None:
            calls.append("commit")

        async def refresh(self, _instance: object) -> None:
            calls.append("refresh")

        def rollback(self) -> None:
            calls.append("rollback")

    db = Db()
    pre_handler = phase_db.PhaseDb(
        db,
        phase="PRE_HANDLER",
        caps=phase_db.phase_db_capabilities("PRE_HANDLER"),
        owns_tx=True,
    )

    asyncio.run(pre_handler.flush())
    with pytest.raises(RuntimeError, match=r"db.commit\(\) is not allowed"):
        asyncio.run(pre_handler.commit())
    with pytest.raises(RuntimeError, match=r"db.refresh\(\) is not allowed"):
        asyncio.run(pre_handler.refresh(object()))

    post_commit = phase_db.PhaseDb(
        db,
        phase="POST_COMMIT",
        caps=phase_db.phase_db_capabilities("POST_COMMIT"),
        owns_tx=True,
    )
    asyncio.run(post_commit.refresh(object()))
    asyncio.run(post_commit.rollback())

    assert calls == ["flush", "refresh", "rollback"]


def test_phase_db_denies_commit_when_tx_not_owned_even_if_phase_allows_commit() -> None:
    class Db:
        def commit(self) -> None:
            raise AssertionError("commit should not be called")

    wrapper = phase_db.PhaseDb(
        Db(),
        phase="END_TX",
        caps=phase_db.phase_db_capabilities("END_TX"),
        owns_tx=False,
    )

    with pytest.raises(RuntimeError, match=r"db.commit\(\) is not allowed"):
        asyncio.run(wrapper.commit())


def test_resolve_db_handle_prefers_db_and_falls_back_to_session() -> None:
    db = object()
    session = object()

    both_ctx = SimpleNamespace(db=db, session=session)
    session_only_ctx = SimpleNamespace(session=session)

    assert _db._resolve_db_handle(both_ctx) is db
    assert _db._resolve_db_handle(session_only_ctx) is session


def test_is_async_db_detects_run_sync_or_async_methods() -> None:
    class WithRunSync:
        def run_sync(self) -> None:
            return None

    class WithAsyncCommit:
        async def commit(self) -> None:
            return None

    class SyncOnly:
        def commit(self) -> None:
            return None

    assert _db._is_async_db(WithRunSync()) is True
    assert _db._is_async_db(WithAsyncCommit()) is True
    assert _db._is_async_db(SyncOnly()) is False
    assert _db._is_async_db(None) is False


def test_in_transaction_checks_callable_and_truthy_attributes() -> None:
    class CallableTrue:
        def in_transaction(self) -> bool:
            return True

    class CallableRaises:
        def in_transaction(self) -> bool:
            raise RuntimeError("boom")

        in_nested_transaction = True

    class AttrOnly:
        in_nested_transaction = 1

    assert _db._in_transaction(CallableTrue()) is True
    assert _db._in_transaction(CallableRaises()) is True
    assert _db._in_transaction(AttrOnly()) is True
    assert _db._in_transaction(SimpleNamespace()) is False
    assert _db._in_transaction(None) is False
