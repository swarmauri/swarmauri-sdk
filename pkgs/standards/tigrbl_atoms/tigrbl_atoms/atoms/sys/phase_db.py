from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...phases import PhaseName


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


@dataclass(frozen=True, slots=True)
class DbCapabilities:
    allow_flush: bool
    allow_commit: bool
    commit_requires_owned_tx: bool
    allow_refresh: bool = False


_PHASE_DB_CAPABILITIES: dict[PhaseName, DbCapabilities] = {
    "INGRESS_BEGIN": DbCapabilities(False, False, True, False),
    "INGRESS_PARSE": DbCapabilities(False, False, True, False),
    "INGRESS_DISPATCH": DbCapabilities(False, False, True, False),
    "PRE_TX_BEGIN": DbCapabilities(False, False, True, False),
    "START_TX": DbCapabilities(False, False, True, False),
    "PRE_HANDLER": DbCapabilities(True, False, True, False),
    "HANDLER": DbCapabilities(True, True, True, False),
    "POST_HANDLER": DbCapabilities(True, False, True, False),
    "PRE_COMMIT": DbCapabilities(False, False, True, False),
    "END_TX": DbCapabilities(True, True, True, False),
    "POST_COMMIT": DbCapabilities(True, False, True, True),
    "POST_RESPONSE": DbCapabilities(False, False, True, False),
    "EGRESS_SHAPE": DbCapabilities(False, False, True, False),
    "EGRESS_FINALIZE": DbCapabilities(False, False, True, False),
    "ON_ERROR": DbCapabilities(False, False, True, False),
    "ON_PRE_TX_BEGIN_ERROR": DbCapabilities(False, False, True, False),
    "ON_START_TX_ERROR": DbCapabilities(False, False, True, False),
    "ON_PRE_HANDLER_ERROR": DbCapabilities(False, False, True, False),
    "ON_HANDLER_ERROR": DbCapabilities(False, False, True, False),
    "ON_POST_HANDLER_ERROR": DbCapabilities(False, False, True, False),
    "ON_PRE_COMMIT_ERROR": DbCapabilities(False, False, True, False),
    "ON_END_TX_ERROR": DbCapabilities(False, False, True, False),
    "ON_POST_COMMIT_ERROR": DbCapabilities(False, False, True, False),
    "ON_POST_RESPONSE_ERROR": DbCapabilities(False, False, True, False),
    "ON_ROLLBACK": DbCapabilities(False, False, True, False),
}


def phase_db_capabilities(phase: str) -> DbCapabilities:
    try:
        return _PHASE_DB_CAPABILITIES[phase]  # type: ignore[index]
    except KeyError as exc:  # pragma: no cover
        raise RuntimeError(f"Unknown phase for PhaseDb binding: {phase!r}") from exc


class PhaseDb:
    __slots__ = ("_db", "_phase", "_caps", "_owns_tx")

    def __init__(
        self,
        db: Any,
        *,
        phase: str,
        caps: DbCapabilities,
        owns_tx: bool,
    ) -> None:
        self._db = db
        self._phase = phase
        self._caps = caps
        self._owns_tx = owns_tx

    @property
    def raw(self) -> Any:
        return self._db

    def _deny(self, op: str) -> RuntimeError:
        return RuntimeError(f"db.{op}() is not allowed during {self._phase} phase")

    async def flush(self) -> None:
        if not self._caps.allow_flush:
            raise self._deny("flush")
        await _maybe_await(self._db.flush())

    async def commit(self) -> None:
        if not self._caps.allow_commit:
            raise self._deny("commit")
        if self._caps.commit_requires_owned_tx and not self._owns_tx:
            raise self._deny("commit")
        await _maybe_await(self._db.commit())

    async def refresh(self, instance: Any) -> None:
        if not self._caps.allow_refresh:
            raise self._deny("refresh")
        await _maybe_await(self._db.refresh(instance))

    async def rollback(self) -> None:
        await _maybe_await(self._db.rollback())

    def __getattr__(self, name: str) -> Any:
        return getattr(self._db, name)


def bind_phase_db(ctx: Any) -> Any:
    raw_db = getattr(ctx, "_raw_db", None)
    if raw_db is None:
        ctx.db = None
        return ctx

    phase = getattr(ctx, "phase", None)
    if not isinstance(phase, str) or not phase:
        raise RuntimeError("ctx.phase must be set before PhaseDb binding")

    owns_tx = bool(getattr(ctx, "owns_tx", False))
    temp = getattr(ctx, "temp", None)
    cache_token = (id(raw_db), owns_tx)
    cache: dict[str, PhaseDb] | None = None
    if isinstance(temp, dict):
        cached_token = temp.get("_phase_db_cache_token")
        if cached_token == cache_token:
            maybe_cache = temp.get("_phase_db_cache")
            if isinstance(maybe_cache, dict):
                cache = maybe_cache
        else:
            temp["_phase_db_cache_token"] = cache_token
            temp["_phase_db_cache"] = {}
            cache = temp["_phase_db_cache"]

    if cache is not None:
        wrapped = cache.get(phase)
        if wrapped is None:
            wrapped = PhaseDb(
                raw_db,
                phase=phase,
                caps=phase_db_capabilities(phase),
                owns_tx=owns_tx,
            )
            cache[phase] = wrapped
        ctx.db = wrapped
        return ctx

    ctx.db = PhaseDb(
        raw_db,
        phase=phase,
        caps=phase_db_capabilities(phase),
        owns_tx=owns_tx,
    )
    return ctx


def run(ctx: Any) -> Any:
    return bind_phase_db(ctx)


__all__ = ["DbCapabilities", "PhaseDb", "bind_phase_db", "phase_db_capabilities", "run"]
