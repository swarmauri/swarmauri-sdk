"""Database session guard utilities for the runtime executor.

This module temporarily replaces ``commit`` and ``flush`` on SQLAlchemy
sessions to enforce phase-specific policies. Each guard returns a handle that
restores the original methods once the phase completes and provides helpers to
rollback when the runtime owns the transaction.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Union

try:
    from sqlalchemy.orm import Session  # type: ignore
    from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
except Exception:  # pragma: no cover
    Session = Any  # type: ignore
    AsyncSession = Any  # type: ignore

from .types import _Ctx, PhaseChains
from .helpers import _is_async_db, _run_chain, _g

logger = logging.getLogger(__name__)


class _GuardHandle:
    """Stores original ``commit``/``flush`` methods for later restoration."""

    __slots__ = ("db", "orig_commit", "orig_flush")

    def __init__(self, db: Any, orig_commit: Any, orig_flush: Any) -> None:
        self.db = db
        self.orig_commit = orig_commit
        self.orig_flush = orig_flush

    def restore(self) -> None:
        if self.orig_commit is not None:
            try:
                setattr(self.db, "commit", self.orig_commit)
            except Exception:
                pass  # pragma: no cover
        if self.orig_flush is not None:
            try:
                setattr(self.db, "flush", self.orig_flush)
            except Exception:
                pass  # pragma: no cover


def _install_db_guards(
    db: Union[Session, AsyncSession, None],
    *,
    phase: str,
    allow_flush: bool,
    allow_commit: bool,
    require_owned_tx_for_commit: bool,
    owns_tx: bool,
) -> _GuardHandle:
    """Install guards that restrict ``commit``/``flush`` during a phase.

    Parameters:
        db: SQLAlchemy ``Session``/``AsyncSession`` to guard.
        phase: Name of the executing phase for error messages.
        allow_flush: Whether ``flush`` should be permitted.
        allow_commit: Whether ``commit`` should be permitted.
        require_owned_tx_for_commit: Block commits if the executor did not
            open the transaction.
        owns_tx: Whether the runtime opened the transaction.

    Returns:
        A ``_GuardHandle`` for restoring original methods.
    """
    if db is None:
        return _GuardHandle(None, None, None)
    orig_commit = getattr(db, "commit", None)
    orig_flush = getattr(db, "flush", None)

    def _raise(op: str) -> None:
        raise RuntimeError(f"db.{op}() is not allowed during {phase} phase")

    if not allow_commit or (require_owned_tx_for_commit and not owns_tx):
        if _is_async_db(db):

            async def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")
        else:

            def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")

        setattr(db, "commit", _blocked_commit)  # type: ignore[assignment]

    if not allow_flush:
        if _is_async_db(db):

            async def _blocked_flush() -> None:  # type: ignore[func-returns-value]
                _raise("flush")
        else:

            def _blocked_flush() -> None:  # type: ignore[func-returns-value]
                _raise("flush")

        setattr(db, "flush", _blocked_flush)  # type: ignore[assignment]

    return _GuardHandle(db, orig_commit, orig_flush)


async def _rollback_if_owned(
    db: Union[Session, AsyncSession, None],
    owns_tx: bool,
    *,
    phases: Optional[PhaseChains],
    ctx: _Ctx,
) -> None:
    """Rollback the session if this runtime owns the transaction."""

    if not owns_tx or db is None:
        return
    try:
        if _is_async_db(db):
            await db.rollback()  # type: ignore[func-returns-value]
        else:
            db.rollback()
    except Exception as rb_exc:  # pragma: no cover
        logger.exception("Rollback failed: %s", rb_exc)
    try:
        await _run_chain(ctx, _g(phases, "ON_ROLLBACK"), phase="ON_ROLLBACK")
    except Exception:  # pragma: no cover
        pass


__all__ = ["_GuardHandle", "_install_db_guards", "_rollback_if_owned"]
