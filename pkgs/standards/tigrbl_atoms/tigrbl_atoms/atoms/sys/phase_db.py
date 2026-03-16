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
    "HANDLER": DbCapabilities(True, False, True, False),
    "POST_HANDLER": DbCapabilities(True, False, True, False),
    "PRE_COMMIT": DbCapabilities(False, False, True, False),
    "END_TX": DbCapabilities(True, True, True, False),
    "POST_COMMIT": DbCapabilities(True, False, True, True),
    "POST_RESPONSE": DbCapabilities(False, False, True, False),
    "EGRESS_SHAPE": DbCapabilities(False, False, True, False),
    "EGRESS_FINALIZE": DbCapabilities(False, False, True, False),
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


def bind_phase_db(ctx: Any) -> None:
    raw_db = getattr(ctx, "_raw_db", None)
    if raw_db is None:
        ctx.db = None
        return None

    phase = getattr(ctx, "phase", None)
    if not isinstance(phase, str) or not phase:
        raise RuntimeError("ctx.phase must be set before PhaseDb binding")

    caps = phase_db_capabilities(phase)
    owns_tx = bool(getattr(ctx, "owns_tx", False))
    ctx.db = PhaseDb(raw_db, phase=phase, caps=caps, owns_tx=owns_tx)
    return None


def run(ctx: Any) -> None:
    return bind_phase_db(ctx)


__all__ = ["DbCapabilities", "PhaseDb", "bind_phase_db", "phase_db_capabilities", "run"]
