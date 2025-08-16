# autoapi/v3/runtime/executor.py
from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Union,
    Protocol,
    runtime_checkable,
)
import inspect
import logging

try:
    from fastapi import Request  # type: ignore
except Exception:  # pragma: no cover
    Request = Any  # type: ignore

try:
    from sqlalchemy.orm import Session  # type: ignore
    from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
except Exception:  # pragma: no cover
    Session = Any  # type: ignore
    AsyncSession = Any  # type: ignore

from .errors import create_standardized_error
from ..config.constants import CTX_SKIP_PERSIST_FLAG

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────────────────────────
# Types
# ───────────────────────────────────────────────────────────────────────────────


@runtime_checkable
class _Step(Protocol):
    def __call__(self, ctx: "_Ctx") -> Union[Any, Awaitable[Any]]: ...


HandlerStep = Union[_Step, Callable[["_Ctx"], Any], Callable[["_Ctx"], Awaitable[Any]]]
PhaseChains = Mapping[
    str, Sequence[HandlerStep]
]  # {"HANDLER": [...], "COMMIT": [...], ...}


class _Ctx(dict):
    """
    Dict-like context with attribute access. Common keys:
      • request: FastAPI Request (optional)
      • db: Session | AsyncSession
      • api/model/op: optional metadata
      • result: last non-None step result
      • error: last exception caught (on failure paths)
      • response: SimpleNamespace(result=...) for POST_RESPONSE shaping
    """

    __slots__ = ()
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

    @classmethod
    def ensure(
        cls,
        *,
        request: Optional[Request],
        db: Union[Session, AsyncSession, None],
        seed: Optional[MutableMapping[str, Any]] = None,
    ) -> "_Ctx":
        ctx = cls() if seed is None else (seed if isinstance(seed, _Ctx) else cls(seed))
        if request is not None:
            ctx.request = request
            state = getattr(request, "state", None)
            if state is not None and getattr(state, "ctx", None) is None:
                try:
                    state.ctx = ctx  # make ctx available to deps
                except Exception:  # pragma: no cover
                    pass
        if db is not None:
            ctx.db = db
        return ctx


# ───────────────────────────────────────────────────────────────────────────────
# Introspection & helpers
# ───────────────────────────────────────────────────────────────────────────────


def _is_async_db(db: Any) -> bool:
    """Detect DB interfaces that require ``await`` for transactional methods."""

    if isinstance(db, AsyncSession) or hasattr(db, "run_sync"):
        return True
    for attr in ("commit", "begin"):
        if inspect.iscoroutinefunction(getattr(db, attr, None)):
            return True
    return False


def _bool_call(meth: Any) -> bool:
    try:
        return bool(meth())
    except Exception:  # pragma: no cover
        return False


def _in_tx(db: Any) -> bool:
    for name in ("in_transaction", "in_nested_transaction"):
        attr = getattr(db, name, None)
        if callable(attr):
            if _bool_call(attr):
                return True
        elif attr:
            return True
    return False


async def _maybe_await(v: Any) -> Any:
    if hasattr(v, "__await__"):
        return await v  # type: ignore[func-returns-value]
    return v


async def _run_chain(ctx: _Ctx, chain: Optional[Iterable[HandlerStep]]) -> None:
    if not chain:
        return
    for step in chain:
        rv = step(ctx)
        rv = await _maybe_await(rv)
        if rv is not None:
            ctx.result = rv  # last non-None wins


def _g(phases: Optional[PhaseChains], key: str) -> Sequence[HandlerStep]:
    return () if not phases else phases.get(key, ())


# ───────────────────────────────────────────────────────────────────────────────
# DB guards (enforce per-phase flush/commit policy)
# ───────────────────────────────────────────────────────────────────────────────


class _GuardHandle:
    __slots__ = ("db", "orig_commit", "orig_flush")

    def __init__(self, db: Any, orig_commit: Any, orig_flush: Any) -> None:
        self.db = db
        self.orig_commit = orig_commit
        self.orig_flush = orig_flush

    def restore(self) -> None:
        if self.orig_commit is not None:
            try:
                setattr(self.db, "commit", self.orig_commit)
            except Exception:  # pragma: no cover
                pass
        if self.orig_flush is not None:
            try:
                setattr(self.db, "flush", self.orig_flush)
            except Exception:  # pragma: no cover
                pass


def _install_db_guards(
    db: Union[Session, AsyncSession, None],
    *,
    phase: str,
    allow_flush: bool,
    allow_commit: bool,
    require_started_tx_for_commit: bool,
    started_tx: bool,
) -> _GuardHandle:
    """
    Monkey-patch db.commit/db.flush during a phase to enforce policy.
    We assign simple callables on the instance so they are invoked without `self`.
    """
    if db is None:
        return _GuardHandle(None, None, None)
    orig_commit = getattr(db, "commit", None)
    orig_flush = getattr(db, "flush", None)

    def _raise(op: str) -> None:
        raise RuntimeError(f"db.{op}() is not allowed during {phase} phase")

    # commit wrapper
    if not allow_commit:
        if _is_async_db(db):

            async def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")
        else:

            def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")

        setattr(db, "commit", _blocked_commit)  # type: ignore[assignment]
    else:
        # allow commit, but optionally require that *this* run started the txn
        if require_started_tx_for_commit and not started_tx:
            if _is_async_db(db):

                async def _blocked_commit_started() -> None:  # type: ignore[func-returns-value]
                    _raise("commit")
            else:

                def _blocked_commit_started() -> None:  # type: ignore[func-returns-value]
                    _raise("commit")

            setattr(db, "commit", _blocked_commit_started)  # type: ignore[assignment]

    # flush wrapper
    if not allow_flush:
        if _is_async_db(db):

            async def _blocked_flush() -> None:  # type: ignore[func-returns-value]
                _raise("flush")
        else:

            def _blocked_flush() -> None:  # type: ignore[func-returns-value]
                _raise("flush")

        setattr(db, "flush", _blocked_flush)  # type: ignore[assignment]

    return _GuardHandle(db, orig_commit, orig_flush)


async def _rollback_if_started(
    db: Union[Session, AsyncSession],
    started_tx: bool,
    *,
    phases: Optional[PhaseChains],
    ctx: _Ctx,
) -> None:
    if not started_tx:
        return
    try:
        if _is_async_db(db):
            await db.rollback()  # type: ignore[func-returns-value]
        else:
            db.rollback()
    except Exception as rb_exc:  # pragma: no cover
        logger.exception("Rollback failed: %s", rb_exc)
    # best-effort rollback hooks
    try:
        await _run_chain(ctx, _g(phases, "ON_ROLLBACK"))
    except Exception:  # pragma: no cover
        pass


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession],
    phases: Optional[PhaseChains],  # must include at least "HANDLER"
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """
    Execute an operation through explicit phases with strict write policies.

    Required (typical) phases:
      PRE_TX_BEGIN? → TX_BEGIN → PRE_HANDLER → HANDLER → POST_HANDLER → PRE_COMMIT → COMMIT → POST_COMMIT → POST_RESPONSE

    Guard policies:
      • PRE_HANDLER, HANDLER, POST_HANDLER: flush-only (commit forbidden)
      • PRE_COMMIT, POST_COMMIT: no writes (flush & commit forbidden)
      • COMMIT: commit allowed (and usually executed by a default hook)
      • If `skip_persist` is true: no writes anywhere and TX_BEGIN/COMMIT are skipped.

    Error handling:
      • Each phase maps to ON_<PHASE>_ERROR (if present) else ON_ERROR.
      • Phases inside the txn trigger rollback if this run opened the txn, then ON_ROLLBACK.
      • POST_RESPONSE remains non-fatal; errors are reported but the prior result is returned.
    """
    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))

    existed_tx_before = _in_tx(db)
    started_tx = False  # computed after TX_BEGIN

    # Helper to run a guarded phase
    async def _run_phase(
        name: str,
        *,
        allow_flush: bool,
        allow_commit: bool,
        in_tx: bool,
        require_started_for_commit: bool = True,
        nonfatal: bool = False,
    ) -> None:
        chain = _g(phases, name)
        if not chain:
            return

        # If skip_persist, no writes anywhere
        eff_allow_flush = allow_flush and (not skip_persist)
        eff_allow_commit = allow_commit and (not skip_persist)

        guard = _install_db_guards(
            db,
            phase=name,
            allow_flush=eff_allow_flush,
            allow_commit=eff_allow_commit,
            require_started_tx_for_commit=require_started_for_commit,
            started_tx=started_tx,
        )

        try:
            await _run_chain(ctx, chain)
        except Exception as exc:
            ctx.error = exc
            # rollback only for phases that run inside a txn
            if in_tx:
                await _rollback_if_started(db, started_tx, phases=phases, ctx=ctx)
            # run phase-specific error hooks (or ON_ERROR)
            err_name = f"ON_{name}_ERROR"
            try:
                await _run_chain(ctx, _g(phases, err_name) or _g(phases, "ON_ERROR"))
            except Exception:  # pragma: no cover
                pass
            if nonfatal:
                # report and continue (POST_RESPONSE)
                logger.exception("%s failed (nonfatal): %s", name, exc)
                return
            raise create_standardized_error(exc)
        finally:
            guard.restore()

    # ─── PRE_TX_BEGIN (outside txn) ────────────────────────────────────────────
    await _run_phase("PRE_TX_BEGIN", allow_flush=False, allow_commit=False, in_tx=False)

    # ─── TX_BEGIN (begin txn via hooks; skip when skip_persist) ────────────────
    if not skip_persist:
        await _run_phase(
            "START_TX",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            require_started_for_commit=True,
        )
    # compute if *this* run started the transaction
    started_tx = (not existed_tx_before) and _in_tx(db)

    # ─── PRE_HANDLER (flush-only) ──────────────────────────────────────────────
    await _run_phase(
        "PRE_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    # ─── HANDLER (flush-only; core lives here) ─────────────────────────────────
    await _run_phase(
        "HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    # ─── POST_HANDLER (flush-only) ─────────────────────────────────────────────
    await _run_phase(
        "POST_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    # ─── PRE_COMMIT (no writes) ────────────────────────────────────────────────
    await _run_phase(
        "PRE_COMMIT", allow_flush=False, allow_commit=False, in_tx=not skip_persist
    )

    # ─── COMMIT (commit-only hooks; skip when skip_persist) ────────────────────
    if not skip_persist:
        await _run_phase(
            "END_TX",
            allow_flush=True,  # a final flush right before commit is OK
            allow_commit=True,  # commit allowed
            in_tx=True,
            require_started_for_commit=True,
        )

    # ─── POST_COMMIT (no writes) ───────────────────────────────────────────────
    await _run_phase("POST_COMMIT", allow_flush=False, allow_commit=False, in_tx=False)

    # ─── POST_RESPONSE (non-fatal) ─────────────────────────────────────────────
    from types import SimpleNamespace as _NS

    ctx.response = _NS(result=ctx.get("result"))
    await _run_phase(
        "POST_RESPONSE",
        allow_flush=False,
        allow_commit=False,
        in_tx=False,
        nonfatal=True,
    )
    return ctx.response.result


__all__ = ["_Ctx", "_invoke"]
