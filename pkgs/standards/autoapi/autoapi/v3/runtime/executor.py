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

# Optional tracing: executor works fine without it
try:
    from . import trace as _trace  # type: ignore
except Exception:  # pragma: no cover
    _trace = None  # type: ignore

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
PhaseChains = Mapping[str, Sequence[HandlerStep]]  # {"HANDLER": [...], ...}


class _Ctx(dict):
    """
    Dict-like context with attribute access. Common keys:
      • request: FastAPI Request (optional)
      • db: Session | AsyncSession
      • api/model/op: optional metadata
      • result: last non-None step result
      • error: last exception caught (on failure paths)
      • response: SimpleNamespace(result=...) for POST_RESPONSE shaping
      • temp: scratch dict used by atoms/hook steps
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
        # Ensure temp scratch exists for atoms/system steps/hooks
        if "temp" not in ctx or not isinstance(ctx.get("temp"), dict):
            ctx.temp = {}
        return ctx


# ───────────────────────────────────────────────────────────────────────────────
# Introspection & helpers
# ───────────────────────────────────────────────────────────────────────────────


def _is_async_db(db: Any) -> bool:
    """Detect DB interfaces that require `await` for transactional methods."""
    if isinstance(db, AsyncSession) or hasattr(db, "run_sync"):
        return True
    for attr in ("commit", "begin", "rollback", "flush"):
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
    if inspect.isawaitable(v):
        return await v  # type: ignore[func-returns-value]
    return v


async def _run_chain(
    ctx: _Ctx, chain: Optional[Iterable[HandlerStep]], *, phase: str
) -> None:
    if not chain:
        return
    # Optional phase-level tracing
    if _trace is not None:
        with _trace.span(ctx, f"phase:{phase}"):
            for step in chain:
                rv = step(ctx)
                rv = await _maybe_await(rv)
                if rv is not None:
                    ctx.result = rv
        return
    # No tracing
    for step in chain:
        rv = step(ctx)
        rv = await _maybe_await(rv)
        if rv is not None:
            ctx.result = rv


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
    if not allow_commit or (require_owned_tx_for_commit and not owns_tx):
        if _is_async_db(db):

            async def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")
        else:

            def _blocked_commit() -> None:  # type: ignore[func-returns-value]
                _raise("commit")

        setattr(db, "commit", _blocked_commit)  # type: ignore[assignment]

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


async def _rollback_if_owned(
    db: Union[Session, AsyncSession, None],
    owns_tx: bool,
    *,
    phases: Optional[PhaseChains],
    ctx: _Ctx,
) -> None:
    if not owns_tx or db is None:
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
        await _run_chain(ctx, _g(phases, "ON_ROLLBACK"), phase="ON_ROLLBACK")
    except Exception:  # pragma: no cover
        pass


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession, None],
    phases: Optional[PhaseChains],  # must include at least "HANDLER"
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """
    Execute an operation through explicit phases with strict write policies.

    Typical phases:
      PRE_TX_BEGIN? → START_TX → PRE_HANDLER → HANDLER → POST_HANDLER → END_TX → POST_RESPONSE
    (PRE_COMMIT / POST_COMMIT remain supported if present in the chains)

    Guard policies:
      • PRE_HANDLER, HANDLER, POST_HANDLER: flush-only (commit forbidden)
      • END_TX: commit allowed (and usually executed by a default hook)
      • PRE_COMMIT, POST_COMMIT: no writes (flush & commit forbidden) — optional legacy hooks
      • If `skip_persist`: no writes anywhere; START_TX/END_TX skipped.

    Error handling:
      • Each phase maps to ON_<PHASE>_ERROR (if present) else ON_ERROR.
      • Phases inside an owned txn trigger rollback, then ON_ROLLBACK.
      • POST_RESPONSE is non-fatal; errors are logged and the prior result returned.
    """
    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    # Guard: previous operations may have left the session in a transaction.
    # Ensure we start from a clean state before invoking the lifecycle.
    if db is not None and _in_tx(db):
        try:
            if _is_async_db(db):
                await db.commit()  # type: ignore[attr-defined]
            else:
                db.commit()  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            pass
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))

    # Track whether a transaction existed at entry. If none did, this run "owns" the TX lifecycle.
    existed_tx_before = _in_tx(db) if db is not None else False

    # Helper to run a guarded phase
    async def _run_phase(
        name: str,
        *,
        allow_flush: bool,
        allow_commit: bool,
        in_tx: bool,
        require_owned_for_commit: bool = True,
        nonfatal: bool = False,
        owns_tx_for_phase: Optional[bool] = None,
    ) -> None:
        chain = _g(phases, name)
        if not chain:
            return

        # If skip_persist, no writes anywhere
        eff_allow_flush = allow_flush and (not skip_persist)
        eff_allow_commit = allow_commit and (not skip_persist)

        # Determine "ownership" for this phase (commit allowed only if we own it)
        owns_tx_now = bool(owns_tx_for_phase)
        if owns_tx_for_phase is None:
            # Default: we own the TX iff there was no TX on entry
            owns_tx_now = not existed_tx_before

        guard = _install_db_guards(
            db,
            phase=name,
            allow_flush=eff_allow_flush,
            allow_commit=eff_allow_commit,
            require_owned_tx_for_commit=require_owned_for_commit,
            owns_tx=owns_tx_now,
        )

        try:
            await _run_chain(ctx, chain, phase=name)
        except Exception as exc:
            ctx.error = exc
            # rollback only for phases that run inside a txn AND we own it
            if in_tx:
                await _rollback_if_owned(db, owns_tx_now, phases=phases, ctx=ctx)
            # run phase-specific error hooks (or ON_ERROR)
            err_name = f"ON_{name}_ERROR"
            try:
                await _run_chain(
                    ctx, _g(phases, err_name) or _g(phases, "ON_ERROR"), phase=err_name
                )
            except Exception:  # pragma: no cover
                pass
            if nonfatal:
                logger.exception("%s failed (nonfatal): %s", name, exc)
                return
            raise create_standardized_error(exc)
        finally:
            guard.restore()

    # ─── PRE_TX_BEGIN (outside txn) ────────────────────────────────────────────
    await _run_phase("PRE_TX_BEGIN", allow_flush=False, allow_commit=False, in_tx=False)

    # ─── START_TX (begin txn via hooks; skip when skip_persist) ────────────────
    if not skip_persist:
        await _run_phase(
            "START_TX",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            require_owned_for_commit=True,
        )

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

    # Legacy optional phases (supported if provided)
    await _run_phase(
        "PRE_COMMIT", allow_flush=False, allow_commit=False, in_tx=not skip_persist
    )

    # ─── END_TX (commit) ───────────────────────────────────────────────────────
    if not skip_persist:
        # Recompute ownership right before commit to handle SQLAlchemy 2.x autobegin:
        # We own the TX if none existed at entry AND a TX exists now.
        owns_tx_for_commit = (not existed_tx_before) and (db is not None and _in_tx(db))
        await _run_phase(
            "END_TX",
            allow_flush=True,  # final flush before commit is OK
            allow_commit=True,  # commit allowed
            in_tx=True,
            require_owned_for_commit=True,
            owns_tx_for_phase=owns_tx_for_commit,
        )

    from types import SimpleNamespace as _NS

    # Serialize the result before post-commit hooks so they can mutate the
    # shaped output.
    serializer = ctx.get("response_serializer")
    if callable(serializer):
        try:
            ctx["result"] = serializer(ctx.get("result"))
        except Exception:
            logger.exception("response serialization failed", exc_info=True)
    ctx.response = _NS(result=ctx.get("result"))

    await _run_phase("POST_COMMIT", allow_flush=True, allow_commit=False, in_tx=False)

    await _run_phase(
        "POST_RESPONSE",
        allow_flush=False,
        allow_commit=False,
        in_tx=False,
        nonfatal=True,
    )
    # Defensive: ensure the session is not left in a transactional state. Some
    # backends may implicitly begin a new transaction during commit/flush cycles.
    if db is not None and _in_tx(db):
        try:
            if _is_async_db(db):
                await db.commit()  # type: ignore[attr-defined]
            else:
                db.commit()  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - defensive safeguard
            pass
    return ctx.response.result


__all__ = ["_Ctx", "_invoke"]
