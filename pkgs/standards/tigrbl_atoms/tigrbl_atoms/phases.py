from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Final, Generic, Literal, Tuple, TypeVar

from .stages import (
    Boot,
    Ingress,
    Planned,
    Guarded,
    Executing,
    Resolved,
    Operated,
    Encoded,
    Egressed,
    Failed,
    Stage,
)

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")

PhaseName = Literal[
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_END_TX_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "ON_ROLLBACK",
]


@dataclass(frozen=True)
class PhaseStep(Generic[S, T]):
    name: PhaseName
    stage_in: Stage
    stage_out: Stage
    in_tx: bool = False
    is_error: bool = False


def seq_phase(a: PhaseStep[S, T], b: PhaseStep[T, U]) -> PhaseStep[S, U]:
    return PhaseStep(
        name=f"{a.name}->{b.name}",  # type: ignore
        stage_in=a.stage_in,
        stage_out=b.stage_out,
        in_tx=a.in_tx or b.in_tx,
        is_error=a.is_error or b.is_error,
    )


INGRESS_BEGIN = PhaseStep("INGRESS_BEGIN", Boot, Ingress)
INGRESS_PARSE = PhaseStep("INGRESS_PARSE", Ingress, Ingress)
INGRESS_ROUTE = PhaseStep("INGRESS_ROUTE", Ingress, Planned)

PRE_TX_BEGIN = PhaseStep("PRE_TX_BEGIN", Planned, Guarded)

START_TX = PhaseStep("START_TX", Guarded, Executing, in_tx=True)
PRE_HANDLER = PhaseStep("PRE_HANDLER", Executing, Resolved, in_tx=True)
HANDLER = PhaseStep("HANDLER", Resolved, Operated, in_tx=True)
POST_HANDLER = PhaseStep("POST_HANDLER", Operated, Operated, in_tx=True)
PRE_COMMIT = PhaseStep("PRE_COMMIT", Operated, Operated, in_tx=True)
END_TX = PhaseStep("END_TX", Operated, Operated, in_tx=True)

POST_COMMIT = PhaseStep("POST_COMMIT", Operated, Encoded)
EGRESS_SHAPE = PhaseStep("EGRESS_SHAPE", Encoded, Encoded)
EGRESS_FINALIZE = PhaseStep("EGRESS_FINALIZE", Encoded, Egressed)
POST_RESPONSE = PhaseStep("POST_RESPONSE", Egressed, Egressed)


ON_ERROR = PhaseStep("ON_ERROR", Failed, Failed, is_error=True)
ON_PRE_TX_BEGIN_ERROR = PhaseStep(
    "ON_PRE_TX_BEGIN_ERROR", Failed, Failed, is_error=True
)
ON_START_TX_ERROR = PhaseStep(
    "ON_START_TX_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_PRE_HANDLER_ERROR = PhaseStep(
    "ON_PRE_HANDLER_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_HANDLER_ERROR = PhaseStep(
    "ON_HANDLER_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_POST_HANDLER_ERROR = PhaseStep(
    "ON_POST_HANDLER_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_PRE_COMMIT_ERROR = PhaseStep(
    "ON_PRE_COMMIT_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_END_TX_ERROR = PhaseStep(
    "ON_END_TX_ERROR", Failed, Failed, in_tx=True, is_error=True
)
ON_POST_COMMIT_ERROR = PhaseStep("ON_POST_COMMIT_ERROR", Failed, Failed, is_error=True)
ON_POST_RESPONSE_ERROR = PhaseStep(
    "ON_POST_RESPONSE_ERROR", Failed, Failed, is_error=True
)
ON_ROLLBACK = PhaseStep("ON_ROLLBACK", Failed, Failed, in_tx=True, is_error=True)


PHASES: Final[Tuple[PhaseName, ...]] = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_END_TX_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "ON_ROLLBACK",
)


PHASE_INFO: Final[Dict[PhaseName, PhaseStep]] = {
    p.name: p
    for p in (
        INGRESS_BEGIN,
        INGRESS_PARSE,
        INGRESS_ROUTE,
        PRE_TX_BEGIN,
        START_TX,
        PRE_HANDLER,
        HANDLER,
        POST_HANDLER,
        PRE_COMMIT,
        END_TX,
        POST_COMMIT,
        EGRESS_SHAPE,
        EGRESS_FINALIZE,
        POST_RESPONSE,
        ON_ERROR,
        ON_PRE_TX_BEGIN_ERROR,
        ON_START_TX_ERROR,
        ON_PRE_HANDLER_ERROR,
        ON_HANDLER_ERROR,
        ON_POST_HANDLER_ERROR,
        ON_PRE_COMMIT_ERROR,
        ON_END_TX_ERROR,
        ON_POST_COMMIT_ERROR,
        ON_POST_RESPONSE_ERROR,
        ON_ROLLBACK,
    )
}


def phase_info(name: PhaseName) -> PhaseStep:
    try:
        return PHASE_INFO[name]
    except KeyError as e:
        raise ValueError(f"Unknown phase: {name!r}") from e


def phase_stage_in(name: PhaseName) -> Stage:
    return phase_info(name).stage_in


def phase_stage_out(name: PhaseName) -> Stage:
    return phase_info(name).stage_out


__all__ = [
    "PhaseStep",
    "seq_phase",
    "PHASES",
    "PHASE_INFO",
    "phase_info",
    "phase_stage_in",
    "phase_stage_out",
]
