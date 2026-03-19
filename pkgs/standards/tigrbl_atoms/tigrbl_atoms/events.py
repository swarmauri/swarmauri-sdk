from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .phases import (
    EGRESS_FINALIZE_PHASE,
    EGRESS_SHAPE_PHASE,
    END_TX_PHASE,
    HANDLER_PHASE,
    INGRESS_BEGIN_PHASE,
    INGRESS_DISPATCH_PHASE,
    INGRESS_PARSE_PHASE,
    PHASES,
    POST_COMMIT_PHASE,
    POST_HANDLER_PHASE,
    POST_RESPONSE_PHASE,
    PRE_COMMIT_PHASE,
    PRE_HANDLER_PHASE,
    PRE_TX_BEGIN_PHASE,
    START_TX_PHASE,
    PhaseName,
    phase_info,
)
from .stages import (
    Guarded,
    Boot,
    Bound,
    Egressed,
    Emitting,
    Encoded,
    Executing,
    Ingress,
    Operated,
    Resolved,
    Planned,
    Stage,
    stage_ordinal,
)

Phase = PhaseName

INGRESS_BEGIN: Phase = INGRESS_BEGIN_PHASE
INGRESS_PARSE: Phase = INGRESS_PARSE_PHASE
INGRESS_DISPATCH: Phase = INGRESS_DISPATCH_PHASE
PRE_TX_BEGIN: Phase = PRE_TX_BEGIN_PHASE
START_TX: Phase = START_TX_PHASE
PRE_HANDLER: Phase = PRE_HANDLER_PHASE
POST_HANDLER: Phase = POST_HANDLER_PHASE
PRE_COMMIT: Phase = PRE_COMMIT_PHASE
END_TX: Phase = END_TX_PHASE
POST_COMMIT: Phase = POST_COMMIT_PHASE
EGRESS_SHAPE: Phase = EGRESS_SHAPE_PHASE
EGRESS_FINALIZE: Phase = EGRESS_FINALIZE_PHASE
POST_RESPONSE: Phase = POST_RESPONSE_PHASE

INGRESS_CTX_INIT = "ingress.ctx.init"
INGRESS_TRANSPORT_EXTRACT = "ingress.transport.extract"
INGRESS_INPUT_PREPARE = "ingress.input.prepare"

DISPATCH_BINDING_MATCH = "dispatch.binding.match"
DISPATCH_BINDING_PARSE = "dispatch.binding.parse"
DISPATCH_INPUT_NORMALIZE = "dispatch.input.normalize"
DISPATCH_OP_RESOLVE = "dispatch.op.resolve"

DEP_SECURITY = "dep:security"
DEP_EXTRA = "dep:extra"
SYS_TX_BEGIN = "sys.tx.begin"

SCHEMA_COLLECT_IN = "schema:collect_in"
IN_VALIDATE = "in:validate"
RESOLVE_VALUES = "resolve:values"
PRE_FLUSH = "pre:flush"
EMIT_ALIASES_PRE = "emit:aliases:pre_flush"

HANDLER = "HANDLER"
SYS_HANDLER_PERSISTENCE = "sys.handler.persistence"

SYS_TX_COMMIT = "sys.tx.commit"

POST_FLUSH = "post:flush"
EMIT_ALIASES_POST = "emit:aliases:post_refresh"
SCHEMA_COLLECT_OUT = "schema:collect_out"
OUT_BUILD = "out:build"
EMIT_ALIASES_READ = "emit:aliases:readtime"
OUT_DUMP = "out:dump"

EGRESS_RESULT_NORMALIZE = "egress.result.normalize"
EGRESS_OUT_DUMP = "egress.out.dump"
EGRESS_ENVELOPE_APPLY = "egress.envelope.apply"
EGRESS_HEADERS_APPLY = "egress.headers.apply"

EGRESS_HTTP_FINALIZE = "egress.http.finalize"
EGRESS_TO_TRANSPORT_RESPONSE = "egress.to_transport_response"
EGRESS_ASGI_SEND = "egress.asgi.send"

_EVENT_ORDER: Tuple[str, ...] = (
    INGRESS_CTX_INIT,
    INGRESS_TRANSPORT_EXTRACT,
    INGRESS_INPUT_PREPARE,
    DISPATCH_BINDING_MATCH,
    DISPATCH_BINDING_PARSE,
    DISPATCH_INPUT_NORMALIZE,
    DISPATCH_OP_RESOLVE,
    DEP_SECURITY,
    DEP_EXTRA,
    SYS_TX_BEGIN,
    SCHEMA_COLLECT_IN,
    IN_VALIDATE,
    RESOLVE_VALUES,
    PRE_FLUSH,
    EMIT_ALIASES_PRE,
    HANDLER,
    SYS_HANDLER_PERSISTENCE,
    SYS_TX_COMMIT,
    POST_FLUSH,
    EMIT_ALIASES_POST,
    SCHEMA_COLLECT_OUT,
    OUT_BUILD,
    EMIT_ALIASES_READ,
    OUT_DUMP,
    EGRESS_RESULT_NORMALIZE,
    EGRESS_OUT_DUMP,
    EGRESS_ENVELOPE_APPLY,
    EGRESS_HEADERS_APPLY,
    EGRESS_HTTP_FINALIZE,
    EGRESS_TO_TRANSPORT_RESPONSE,
    EGRESS_ASGI_SEND,
)


@dataclass(frozen=True)
class AnchorInfo:
    name: str
    phase: Phase
    ordinal: int
    persist_tied: bool
    stage_in: Stage
    stage_out: Stage
    in_tx: bool
    is_error: bool


_ANCHOR_PHASE: Dict[str, Phase] = {
    INGRESS_CTX_INIT: INGRESS_BEGIN,
    INGRESS_TRANSPORT_EXTRACT: INGRESS_PARSE,
    INGRESS_INPUT_PREPARE: INGRESS_PARSE,
    DISPATCH_BINDING_MATCH: INGRESS_DISPATCH,
    DISPATCH_BINDING_PARSE: INGRESS_DISPATCH,
    DISPATCH_INPUT_NORMALIZE: INGRESS_DISPATCH,
    DISPATCH_OP_RESOLVE: INGRESS_DISPATCH,
    DEP_SECURITY: PRE_TX_BEGIN,
    DEP_EXTRA: PRE_TX_BEGIN,
    SYS_TX_BEGIN: START_TX,
    SCHEMA_COLLECT_IN: PRE_HANDLER,
    IN_VALIDATE: PRE_HANDLER,
    RESOLVE_VALUES: PRE_HANDLER,
    PRE_FLUSH: PRE_HANDLER,
    EMIT_ALIASES_PRE: PRE_HANDLER,
    HANDLER: HANDLER_PHASE,
    SYS_HANDLER_PERSISTENCE: HANDLER_PHASE,
    SYS_TX_COMMIT: END_TX,
    POST_FLUSH: POST_COMMIT,
    EMIT_ALIASES_POST: POST_COMMIT,
    SCHEMA_COLLECT_OUT: POST_COMMIT,
    OUT_BUILD: POST_COMMIT,
    EMIT_ALIASES_READ: POST_COMMIT,
    OUT_DUMP: POST_COMMIT,
    EGRESS_RESULT_NORMALIZE: EGRESS_SHAPE,
    EGRESS_OUT_DUMP: EGRESS_SHAPE,
    EGRESS_ENVELOPE_APPLY: EGRESS_SHAPE,
    EGRESS_HEADERS_APPLY: EGRESS_SHAPE,
    EGRESS_HTTP_FINALIZE: EGRESS_FINALIZE,
    EGRESS_TO_TRANSPORT_RESPONSE: EGRESS_FINALIZE,
    EGRESS_ASGI_SEND: EGRESS_FINALIZE,
}

_ANCHOR_STAGE: Dict[str, Tuple[Stage, Stage]] = {
    INGRESS_CTX_INIT: (Boot, Boot),
    INGRESS_TRANSPORT_EXTRACT: (Ingress, Ingress),
    INGRESS_INPUT_PREPARE: (Ingress, Ingress),
    DISPATCH_BINDING_MATCH: (Ingress, Bound),
    DISPATCH_BINDING_PARSE: (Bound, Bound),
    DISPATCH_INPUT_NORMALIZE: (Bound, Bound),
    DISPATCH_OP_RESOLVE: (Bound, Planned),
    DEP_SECURITY: (Planned, Guarded),
    DEP_EXTRA: (Guarded, Guarded),
    SYS_TX_BEGIN: (Guarded, Executing),
    SCHEMA_COLLECT_IN: (Executing, Executing),
    IN_VALIDATE: (Executing, Executing),
    RESOLVE_VALUES: (Executing, Resolved),
    PRE_FLUSH: (Resolved, Resolved),
    EMIT_ALIASES_PRE: (Resolved, Resolved),
    HANDLER: (Resolved, Resolved),
    SYS_HANDLER_PERSISTENCE: (Resolved, Operated),
    SYS_TX_COMMIT: (Operated, Operated),
    POST_FLUSH: (Operated, Operated),
    EMIT_ALIASES_POST: (Operated, Operated),
    SCHEMA_COLLECT_OUT: (Operated, Operated),
    OUT_BUILD: (Operated, Encoded),
    EMIT_ALIASES_READ: (Encoded, Encoded),
    OUT_DUMP: (Encoded, Encoded),
    EGRESS_RESULT_NORMALIZE: (Encoded, Encoded),
    EGRESS_OUT_DUMP: (Encoded, Encoded),
    EGRESS_ENVELOPE_APPLY: (Encoded, Encoded),
    EGRESS_HEADERS_APPLY: (Encoded, Encoded),
    EGRESS_HTTP_FINALIZE: (Emitting, Emitting),
    EGRESS_TO_TRANSPORT_RESPONSE: (Emitting, Egressed),
    EGRESS_ASGI_SEND: (Egressed, Egressed),
}

_PERSIST_TIED = {
    SYS_TX_BEGIN,
    RESOLVE_VALUES,
    PRE_FLUSH,
    EMIT_ALIASES_PRE,
    SYS_HANDLER_PERSISTENCE,
    SYS_TX_COMMIT,
    POST_FLUSH,
    EMIT_ALIASES_POST,
}


def _validate_anchor_stage_windows() -> None:
    for anchor, (src, dst) in _ANCHOR_STAGE.items():
        if stage_ordinal(src) > stage_ordinal(dst):
            raise ValueError(
                f"Non-monotonic anchor stage window: {anchor!r} ({src.__name__} -> {dst.__name__})"
            )
        pinfo = phase_info(_ANCHOR_PHASE[anchor])
        if stage_ordinal(src) < stage_ordinal(pinfo.stage_in):
            raise ValueError(
                f"Anchor {anchor!r} enters before phase {pinfo.name}: {src.__name__} < {pinfo.stage_in.__name__}"
            )
        if stage_ordinal(dst) > stage_ordinal(pinfo.stage_out):
            raise ValueError(
                f"Anchor {anchor!r} exits after phase {pinfo.name}: {dst.__name__} > {pinfo.stage_out.__name__}"
            )


_validate_anchor_stage_windows()

_ANCHORS: Dict[str, AnchorInfo] = {
    anchor: AnchorInfo(
        name=anchor,
        phase=_ANCHOR_PHASE[anchor],
        ordinal=idx,
        persist_tied=anchor in _PERSIST_TIED,
        stage_in=_ANCHOR_STAGE[anchor][0],
        stage_out=_ANCHOR_STAGE[anchor][1],
        in_tx=phase_info(_ANCHOR_PHASE[anchor]).in_tx,
        is_error=phase_info(_ANCHOR_PHASE[anchor]).is_error,
    )
    for idx, anchor in enumerate(_EVENT_ORDER)
}


def is_valid_event(anchor: str) -> bool:
    return anchor in _ANCHORS


def phase_for_event(anchor: str) -> Phase:
    try:
        return _ANCHORS[anchor].phase
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def stage_in_for_event(anchor: str) -> Stage:
    try:
        return _ANCHORS[anchor].stage_in
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def stage_out_for_event(anchor: str) -> Stage:
    try:
        return _ANCHORS[anchor].stage_out
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def is_persist_tied(anchor: str) -> bool:
    try:
        return _ANCHORS[anchor].persist_tied
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def is_tx_event(anchor: str) -> bool:
    try:
        return _ANCHORS[anchor].in_tx
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def get_anchor_info(anchor: str) -> AnchorInfo:
    try:
        return _ANCHORS[anchor]
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def all_events_ordered() -> List[str]:
    return list(_EVENT_ORDER)


def events_for_phase(phase: Phase) -> List[str]:
    if phase not in PHASES:
        raise ValueError(f"Unknown phase: {phase!r}")
    return [a for a, info in _ANCHORS.items() if info.phase == phase]


def prune_events_for_persist(anchors: Iterable[str], *, persist: bool) -> List[str]:
    out: List[str] = []
    for a in anchors:
        if not is_valid_event(a):
            raise ValueError(f"Unknown event anchor: {a!r}")
        if not persist and _ANCHORS[a].persist_tied:
            continue
        out.append(a)
    out.sort(key=lambda x: _ANCHORS[x].ordinal)
    return out


def order_events(anchors: Iterable[str]) -> List[str]:
    anchors = list(anchors)
    for a in anchors:
        if a not in _ANCHORS:
            raise ValueError(f"Unknown event anchor: {a!r}")
    anchors.sort(key=lambda x: _ANCHORS[x].ordinal)
    return anchors


__all__ = [
    "Phase",
    "PHASES",
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_DISPATCH",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER_PHASE",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "INGRESS_CTX_INIT",
    "INGRESS_TRANSPORT_EXTRACT",
    "INGRESS_INPUT_PREPARE",
    "DISPATCH_BINDING_MATCH",
    "DISPATCH_BINDING_PARSE",
    "DISPATCH_INPUT_NORMALIZE",
    "DISPATCH_OP_RESOLVE",
    "DEP_SECURITY",
    "DEP_EXTRA",
    "SYS_TX_BEGIN",
    "SCHEMA_COLLECT_IN",
    "IN_VALIDATE",
    "RESOLVE_VALUES",
    "PRE_FLUSH",
    "EMIT_ALIASES_PRE",
    "HANDLER",
    "SYS_HANDLER_PERSISTENCE",
    "SYS_TX_COMMIT",
    "POST_FLUSH",
    "EMIT_ALIASES_POST",
    "SCHEMA_COLLECT_OUT",
    "OUT_BUILD",
    "EMIT_ALIASES_READ",
    "OUT_DUMP",
    "EGRESS_RESULT_NORMALIZE",
    "EGRESS_OUT_DUMP",
    "EGRESS_ENVELOPE_APPLY",
    "EGRESS_HEADERS_APPLY",
    "EGRESS_HTTP_FINALIZE",
    "EGRESS_TO_TRANSPORT_RESPONSE",
    "EGRESS_ASGI_SEND",
    "AnchorInfo",
    "is_valid_event",
    "phase_for_event",
    "stage_in_for_event",
    "stage_out_for_event",
    "is_persist_tied",
    "is_tx_event",
    "get_anchor_info",
    "all_events_ordered",
    "events_for_phase",
    "prune_events_for_persist",
    "order_events",
]
