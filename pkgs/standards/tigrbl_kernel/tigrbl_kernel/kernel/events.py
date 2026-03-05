# tigrbl/kernel/events.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from tigrbl_typing.phases import PHASES, Phase

# ──────────────────────────────────────────────────────────────────────────────
# Phases
#   - PRE_TX_BEGIN is the pre-transaction phase for security/dependency checks.
#   - START_TX / END_TX are reserved for system steps (no atom anchors there).
#   - Atoms bind only to the event anchors below.
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# Canonical anchors (events) — the only moments atoms can bind to
# Keep these names stable; labels use them directly: step_kind:domain:subject@ANCHOR
# ──────────────────────────────────────────────────────────────────────────────

# Canonical phase name exports (used by harness tests and diagnostics).
INGRESS_BEGIN: Phase = "INGRESS_BEGIN"
INGRESS_PARSE: Phase = "INGRESS_PARSE"
INGRESS_ROUTE: Phase = "INGRESS_ROUTE"

# INGRESS_BEGIN
INGRESS_CTX_INIT = "ingress.ctx.init"
INGRESS_CTX_ATTACH_COMPILED = "ingress.ctx.attach_compiled"
INGRESS_METRICS_START = "ingress.metrics.start"

# INGRESS_PARSE
INGRESS_RAW_FROM_SCOPE = "ingress.raw.from_scope"
INGRESS_METHOD_EXTRACT = "ingress.method.extract"
INGRESS_PATH_EXTRACT = "ingress.path.extract"
INGRESS_REQUEST_FROM_SCOPE = "ingress.request.from_scope"
INGRESS_HEADERS_PARSE = "ingress.headers.parse"
INGRESS_QUERY_PARSE = "ingress.query.parse"
INGRESS_BODY_READ = "ingress.body.read"
INGRESS_REQUEST_BODY_APPLY = "ingress.request.body.apply"
INGRESS_BODY_PEEK = "ingress.body.peek"

# INGRESS_ROUTE
ROUTE_PROTOCOL_DETECT = "route.protocol.detect"
ROUTE_BINDING_MATCH = "route.binding.match"
ROUTE_RPC_ENVELOPE_PARSE = "route.rpc.envelope.parse"
ROUTE_RPC_METHOD_MATCH = "route.rpc.method.match"
ROUTE_OP_RESOLVE = "route.op.resolve"
ROUTE_PATH_PARAMS_EXTRACT = "route.path_params.extract"
ROUTE_PARAMS_NORMALIZE = "route.params.normalize"
ROUTE_PAYLOAD_SELECT = "route.payload.select"
ROUTE_BINDING_POLICY_APPLY = "route.binding.policy.apply"
ROUTE_PLAN_SELECT = "route.plan.select"
ROUTE_CTX_FINALIZE = "route.ctx.finalize"

# PRE_TX_BEGIN
DEP_SECURITY = "dep:security"
DEP_EXTRA = "dep:extra"

# PRE_HANDLER
SCHEMA_COLLECT_IN = "schema:collect_in"
IN_VALIDATE = "in:validate"

# START_TX
SYS_TX_BEGIN = "sys.tx.begin"

# PRE_HANDLER
RESOLVE_VALUES = "resolve:values"
PRE_FLUSH = "pre:flush"
EMIT_ALIASES_PRE = "emit:aliases:pre_flush"

# HANDLER
SYS_HANDLER_PERSISTENCE = "sys.handler.persistence"

# END_TX
SYS_TX_COMMIT = "sys.tx.commit"

# POST_HANDLER
POST_FLUSH = "post:flush"
EMIT_ALIASES_POST = "emit:aliases:post_refresh"
SCHEMA_COLLECT_OUT = "schema:collect_out"
OUT_BUILD = "out:build"

# POST_RESPONSE
EMIT_ALIASES_READ = "emit:aliases:readtime"
OUT_DUMP = "out:dump"

# EGRESS_SHAPE
EGRESS_RESULT_NORMALIZE = "egress.result.normalize"
EGRESS_OUT_DUMP = "egress.out.dump"
EGRESS_ENVELOPE_APPLY = "egress.envelope.apply"
EGRESS_HEADERS_APPLY = "egress.headers.apply"

# EGRESS_FINALIZE
EGRESS_HTTP_FINALIZE = "egress.http.finalize"
EGRESS_TO_TRANSPORT_RESPONSE = "egress.to_transport_response"
EGRESS_ASGI_SEND = "egress.asgi.send"

# Canonical order of event anchors within the request lifecycle.
# This ordering is global and stable; use it to produce deterministic plans/traces.
_EVENT_ORDER: Tuple[str, ...] = (
    # PRE_TX_BEGIN
    INGRESS_CTX_INIT,
    INGRESS_CTX_ATTACH_COMPILED,
    INGRESS_METRICS_START,
    # INGRESS_PARSE
    INGRESS_RAW_FROM_SCOPE,
    INGRESS_METHOD_EXTRACT,
    INGRESS_PATH_EXTRACT,
    INGRESS_REQUEST_FROM_SCOPE,
    INGRESS_HEADERS_PARSE,
    INGRESS_QUERY_PARSE,
    INGRESS_BODY_READ,
    INGRESS_REQUEST_BODY_APPLY,
    INGRESS_BODY_PEEK,
    # INGRESS_ROUTE
    ROUTE_PROTOCOL_DETECT,
    ROUTE_BINDING_MATCH,
    ROUTE_RPC_ENVELOPE_PARSE,
    ROUTE_RPC_METHOD_MATCH,
    ROUTE_OP_RESOLVE,
    ROUTE_PATH_PARAMS_EXTRACT,
    ROUTE_PARAMS_NORMALIZE,
    ROUTE_PAYLOAD_SELECT,
    ROUTE_BINDING_POLICY_APPLY,
    ROUTE_PLAN_SELECT,
    ROUTE_CTX_FINALIZE,
    # PRE_TX_BEGIN
    DEP_SECURITY,
    DEP_EXTRA,
    # PRE_HANDLER
    SCHEMA_COLLECT_IN,
    IN_VALIDATE,
    RESOLVE_VALUES,
    PRE_FLUSH,
    EMIT_ALIASES_PRE,
    # START_TX / HANDLER / END_TX (persistence system steps)
    SYS_TX_BEGIN,
    "HANDLER",
    SYS_HANDLER_PERSISTENCE,
    SYS_TX_COMMIT,
    # POST_HANDLER
    POST_FLUSH,
    EMIT_ALIASES_POST,
    SCHEMA_COLLECT_OUT,
    OUT_BUILD,
    # EGRESS_SHAPE
    EGRESS_RESULT_NORMALIZE,
    EGRESS_OUT_DUMP,
    EGRESS_ENVELOPE_APPLY,
    EGRESS_HEADERS_APPLY,
    # EGRESS_FINALIZE
    EGRESS_HTTP_FINALIZE,
    EGRESS_TO_TRANSPORT_RESPONSE,
    EGRESS_ASGI_SEND,
    # POST_RESPONSE
    EMIT_ALIASES_READ,
    OUT_DUMP,
)


# Map each anchor to its phase and persistence tie.
# "persist_tied=True" means the anchor is pruned for non-persisting ops
# (e.g., read/list) and whenever an op is executed with persist=False.
@dataclass(frozen=True)
class AnchorInfo:
    name: str
    phase: Phase
    ordinal: int
    persist_tied: bool


_ANCHOR_PHASE: Dict[str, Phase] = {
    INGRESS_CTX_INIT: "INGRESS_BEGIN",
    INGRESS_CTX_ATTACH_COMPILED: "INGRESS_BEGIN",
    INGRESS_METRICS_START: "INGRESS_BEGIN",
    INGRESS_RAW_FROM_SCOPE: "INGRESS_PARSE",
    INGRESS_METHOD_EXTRACT: "INGRESS_PARSE",
    INGRESS_PATH_EXTRACT: "INGRESS_PARSE",
    INGRESS_REQUEST_FROM_SCOPE: "INGRESS_PARSE",
    INGRESS_HEADERS_PARSE: "INGRESS_PARSE",
    INGRESS_QUERY_PARSE: "INGRESS_PARSE",
    INGRESS_BODY_READ: "INGRESS_PARSE",
    INGRESS_REQUEST_BODY_APPLY: "INGRESS_PARSE",
    INGRESS_BODY_PEEK: "INGRESS_PARSE",
    ROUTE_PROTOCOL_DETECT: "INGRESS_ROUTE",
    ROUTE_BINDING_MATCH: "INGRESS_ROUTE",
    ROUTE_RPC_ENVELOPE_PARSE: "INGRESS_ROUTE",
    ROUTE_RPC_METHOD_MATCH: "INGRESS_ROUTE",
    ROUTE_OP_RESOLVE: "INGRESS_ROUTE",
    ROUTE_PATH_PARAMS_EXTRACT: "INGRESS_ROUTE",
    ROUTE_PARAMS_NORMALIZE: "INGRESS_ROUTE",
    ROUTE_PAYLOAD_SELECT: "INGRESS_ROUTE",
    ROUTE_BINDING_POLICY_APPLY: "INGRESS_ROUTE",
    ROUTE_PLAN_SELECT: "INGRESS_ROUTE",
    ROUTE_CTX_FINALIZE: "INGRESS_ROUTE",
    DEP_SECURITY: "PRE_TX_BEGIN",
    DEP_EXTRA: "PRE_TX_BEGIN",
    SCHEMA_COLLECT_IN: "PRE_HANDLER",
    IN_VALIDATE: "PRE_HANDLER",
    RESOLVE_VALUES: "PRE_HANDLER",
    SYS_TX_BEGIN: "START_TX",
    PRE_FLUSH: "PRE_HANDLER",
    EMIT_ALIASES_PRE: "PRE_HANDLER",
    "HANDLER": "HANDLER",
    SYS_HANDLER_PERSISTENCE: "HANDLER",
    SYS_TX_COMMIT: "END_TX",
    POST_FLUSH: "POST_HANDLER",
    EMIT_ALIASES_POST: "POST_HANDLER",
    SCHEMA_COLLECT_OUT: "POST_HANDLER",
    OUT_BUILD: "POST_HANDLER",
    EGRESS_RESULT_NORMALIZE: "EGRESS_SHAPE",
    EGRESS_OUT_DUMP: "EGRESS_SHAPE",
    EGRESS_ENVELOPE_APPLY: "EGRESS_SHAPE",
    EGRESS_HEADERS_APPLY: "EGRESS_SHAPE",
    EGRESS_HTTP_FINALIZE: "EGRESS_FINALIZE",
    EGRESS_TO_TRANSPORT_RESPONSE: "EGRESS_FINALIZE",
    EGRESS_ASGI_SEND: "EGRESS_FINALIZE",
    EMIT_ALIASES_READ: "POST_RESPONSE",
    OUT_DUMP: "POST_RESPONSE",
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

_ANCHORS: Dict[str, AnchorInfo] = {
    anchor: AnchorInfo(
        name=anchor,
        phase=_ANCHOR_PHASE[anchor],
        ordinal=idx,
        persist_tied=anchor in _PERSIST_TIED,
    )
    for idx, anchor in enumerate(_EVENT_ORDER)
}


# ──────────────────────────────────────────────────────────────────────────────
# Public helpers
# ──────────────────────────────────────────────────────────────────────────────


def is_valid_event(anchor: str) -> bool:
    """True if the given anchor is one of the canonical events."""
    return anchor in _ANCHORS


def phase_for_event(anchor: str) -> Phase:
    """Return the Phase for a canonical event; raises on unknown anchors."""
    try:
        return _ANCHORS[anchor].phase
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def is_persist_tied(anchor: str) -> bool:
    """Return True if this event is pruned for non-persisting ops."""
    try:
        return _ANCHORS[anchor].persist_tied
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def get_anchor_info(anchor: str) -> AnchorInfo:
    """Return the full :class:`AnchorInfo` for a canonical event."""
    try:
        return _ANCHORS[anchor]
    except KeyError as e:
        raise ValueError(f"Unknown event anchor: {anchor!r}") from e


def all_events_ordered() -> List[str]:
    """Return all canonical events in deterministic, lifecycle order."""
    return list(_EVENT_ORDER)


def events_for_phase(phase: Phase) -> List[str]:
    """Return the subset of events that belong to the given phase."""
    if phase not in PHASES:
        raise ValueError(f"Unknown phase: {phase!r}")
    return [a for a, info in _ANCHORS.items() if info.phase == phase]


def prune_events_for_persist(anchors: Iterable[str], *, persist: bool) -> List[str]:
    """
    Given a sequence of anchors, return a new list with persistence-tied events
    removed when persist=False. Unknown anchors raise ValueError.
    """
    out: List[str] = []
    for a in anchors:
        if not is_valid_event(a):
            raise ValueError(f"Unknown event anchor: {a!r}")
        if not persist and _ANCHORS[a].persist_tied:
            continue
        out.append(a)
    # keep canonical order irrespective of input order
    out.sort(key=lambda x: _ANCHORS[x].ordinal)
    return out


def order_events(anchors: Iterable[str]) -> List[str]:
    """
    Sort a set/list of anchors into canonical lifecycle order.
    Raises on unknown anchors.
    """
    anchors = list(anchors)
    for a in anchors:
        if a not in _ANCHORS:
            raise ValueError(f"Unknown event anchor: {a!r}")
    anchors.sort(key=lambda x: _ANCHORS[x].ordinal)
    return anchors


__all__ = [
    # Phases
    "Phase",
    "PHASES",
    # Anchors (constants)
    "SCHEMA_COLLECT_IN",
    "INGRESS_CTX_INIT",
    "INGRESS_CTX_ATTACH_COMPILED",
    "INGRESS_METRICS_START",
    "INGRESS_RAW_FROM_SCOPE",
    "INGRESS_METHOD_EXTRACT",
    "INGRESS_PATH_EXTRACT",
    "INGRESS_REQUEST_FROM_SCOPE",
    "INGRESS_HEADERS_PARSE",
    "INGRESS_QUERY_PARSE",
    "INGRESS_BODY_READ",
    "INGRESS_REQUEST_BODY_APPLY",
    "INGRESS_BODY_PEEK",
    "ROUTE_PROTOCOL_DETECT",
    "ROUTE_BINDING_MATCH",
    "ROUTE_RPC_ENVELOPE_PARSE",
    "ROUTE_RPC_METHOD_MATCH",
    "ROUTE_OP_RESOLVE",
    "ROUTE_PATH_PARAMS_EXTRACT",
    "ROUTE_PARAMS_NORMALIZE",
    "ROUTE_PAYLOAD_SELECT",
    "ROUTE_BINDING_POLICY_APPLY",
    "ROUTE_PLAN_SELECT",
    "ROUTE_CTX_FINALIZE",
    "IN_VALIDATE",
    "SYS_TX_BEGIN",
    "RESOLVE_VALUES",
    "PRE_FLUSH",
    "EMIT_ALIASES_PRE",
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
    # Types / helpers
    "AnchorInfo",
    "DEP_SECURITY",
    "DEP_EXTRA",
    "is_valid_event",
    "phase_for_event",
    "is_persist_tied",
    "get_anchor_info",
    "all_events_ordered",
    "events_for_phase",
    "prune_events_for_persist",
    "order_events",
]
