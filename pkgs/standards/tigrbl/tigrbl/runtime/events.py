# tigrbl/v3/runtime/events.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Phases
#   - PRE_TX_BEGIN is the pre-transaction phase for security/dependency checks.
#   - START_TX / END_TX are reserved for system steps (no atom anchors there).
#   - Atoms bind only to the event anchors below.
# ──────────────────────────────────────────────────────────────────────────────

Phase = Literal[
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
]

PHASES: Tuple[Phase, ...] = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",  # system-only
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",  # system-only
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
)

# ──────────────────────────────────────────────────────────────────────────────
# Canonical anchors (events) — the only moments atoms can bind to
# Keep these names stable; labels use them directly: step_kind:domain:subject@ANCHOR
# ──────────────────────────────────────────────────────────────────────────────

# INGRESS_BEGIN
INGRESS_CTX_INIT = "ingress.ctx.init"
INGRESS_CTX_ATTACH_COMPILED = "ingress.ctx.attach_compiled"
INGRESS_METRICS_START = "ingress.metrics.start"

# INGRESS_PARSE
INGRESS_METHOD_EXTRACT = "ingress.method.extract"
INGRESS_PATH_EXTRACT = "ingress.path.extract"
INGRESS_HEADERS_PARSE = "ingress.headers.parse"
INGRESS_QUERY_PARSE = "ingress.query.parse"
INGRESS_BODY_READ = "ingress.body.read"
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
DEP_SECURITY = "prex_tx_begin:secdep"
DEP_EXTRA = "prex_tx_begin:dep"

# PRE_HANDLER
SCHEMA_COLLECT_IN = "schema:collect_in"
IN_VALIDATE = "in:validate"

# HANDLER
RESOLVE_VALUES = "resolve:values"
PRE_FLUSH = "pre:flush"
EMIT_ALIASES_PRE = "emit:aliases:pre_flush"

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

# Canonical order of event anchors within the request lifecycle.
# This ordering is global and stable; use it to produce deterministic plans/traces.
_EVENT_ORDER: Tuple[str, ...] = (
    # PRE_TX_BEGIN
    INGRESS_CTX_INIT,
    INGRESS_CTX_ATTACH_COMPILED,
    INGRESS_METRICS_START,
    # INGRESS_PARSE
    INGRESS_METHOD_EXTRACT,
    INGRESS_PATH_EXTRACT,
    INGRESS_HEADERS_PARSE,
    INGRESS_QUERY_PARSE,
    INGRESS_BODY_READ,
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
    # HANDLER
    RESOLVE_VALUES,
    PRE_FLUSH,
    EMIT_ALIASES_PRE,
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


_ANCHORS: Dict[str, AnchorInfo] = {
    # INGRESS_BEGIN (not persist-tied)
    INGRESS_CTX_INIT: AnchorInfo(INGRESS_CTX_INIT, "INGRESS_BEGIN", 0, False),
    INGRESS_CTX_ATTACH_COMPILED: AnchorInfo(
        INGRESS_CTX_ATTACH_COMPILED, "INGRESS_BEGIN", 1, False
    ),
    INGRESS_METRICS_START: AnchorInfo(INGRESS_METRICS_START, "INGRESS_BEGIN", 2, False),
    # INGRESS_PARSE (not persist-tied)
    INGRESS_METHOD_EXTRACT: AnchorInfo(
        INGRESS_METHOD_EXTRACT, "INGRESS_PARSE", 3, False
    ),
    INGRESS_PATH_EXTRACT: AnchorInfo(INGRESS_PATH_EXTRACT, "INGRESS_PARSE", 4, False),
    INGRESS_HEADERS_PARSE: AnchorInfo(INGRESS_HEADERS_PARSE, "INGRESS_PARSE", 5, False),
    INGRESS_QUERY_PARSE: AnchorInfo(INGRESS_QUERY_PARSE, "INGRESS_PARSE", 6, False),
    INGRESS_BODY_READ: AnchorInfo(INGRESS_BODY_READ, "INGRESS_PARSE", 7, False),
    INGRESS_BODY_PEEK: AnchorInfo(INGRESS_BODY_PEEK, "INGRESS_PARSE", 8, False),
    # INGRESS_ROUTE (not persist-tied)
    ROUTE_PROTOCOL_DETECT: AnchorInfo(ROUTE_PROTOCOL_DETECT, "INGRESS_ROUTE", 9, False),
    ROUTE_BINDING_MATCH: AnchorInfo(ROUTE_BINDING_MATCH, "INGRESS_ROUTE", 10, False),
    ROUTE_RPC_ENVELOPE_PARSE: AnchorInfo(
        ROUTE_RPC_ENVELOPE_PARSE, "INGRESS_ROUTE", 11, False
    ),
    ROUTE_RPC_METHOD_MATCH: AnchorInfo(
        ROUTE_RPC_METHOD_MATCH, "INGRESS_ROUTE", 12, False
    ),
    ROUTE_OP_RESOLVE: AnchorInfo(ROUTE_OP_RESOLVE, "INGRESS_ROUTE", 13, False),
    ROUTE_PATH_PARAMS_EXTRACT: AnchorInfo(
        ROUTE_PATH_PARAMS_EXTRACT, "INGRESS_ROUTE", 14, False
    ),
    ROUTE_PARAMS_NORMALIZE: AnchorInfo(
        ROUTE_PARAMS_NORMALIZE, "INGRESS_ROUTE", 15, False
    ),
    ROUTE_PAYLOAD_SELECT: AnchorInfo(ROUTE_PAYLOAD_SELECT, "INGRESS_ROUTE", 16, False),
    ROUTE_BINDING_POLICY_APPLY: AnchorInfo(
        ROUTE_BINDING_POLICY_APPLY, "INGRESS_ROUTE", 17, False
    ),
    ROUTE_PLAN_SELECT: AnchorInfo(ROUTE_PLAN_SELECT, "INGRESS_ROUTE", 18, False),
    ROUTE_CTX_FINALIZE: AnchorInfo(ROUTE_CTX_FINALIZE, "INGRESS_ROUTE", 19, False),
    # PRE_TX_BEGIN (not persist-tied)
    DEP_SECURITY: AnchorInfo(DEP_SECURITY, "PRE_TX_BEGIN", 20, False),
    DEP_EXTRA: AnchorInfo(DEP_EXTRA, "PRE_TX_BEGIN", 21, False),
    # PRE_HANDLER (not persist-tied)
    SCHEMA_COLLECT_IN: AnchorInfo(SCHEMA_COLLECT_IN, "PRE_HANDLER", 22, False),
    IN_VALIDATE: AnchorInfo(IN_VALIDATE, "PRE_HANDLER", 23, False),
    RESOLVE_VALUES: AnchorInfo(RESOLVE_VALUES, "PRE_HANDLER", 24, True),
    PRE_FLUSH: AnchorInfo(PRE_FLUSH, "PRE_HANDLER", 25, True),
    EMIT_ALIASES_PRE: AnchorInfo(EMIT_ALIASES_PRE, "PRE_HANDLER", 26, True),
    # POST_HANDLER (mixed)
    POST_FLUSH: AnchorInfo(POST_FLUSH, "POST_HANDLER", 27, True),
    EMIT_ALIASES_POST: AnchorInfo(EMIT_ALIASES_POST, "POST_HANDLER", 28, True),
    SCHEMA_COLLECT_OUT: AnchorInfo(SCHEMA_COLLECT_OUT, "POST_HANDLER", 29, False),
    OUT_BUILD: AnchorInfo(OUT_BUILD, "POST_HANDLER", 30, False),
    # EGRESS_SHAPE (not persist-tied)
    EGRESS_RESULT_NORMALIZE: AnchorInfo(
        EGRESS_RESULT_NORMALIZE, "EGRESS_SHAPE", 31, False
    ),
    EGRESS_OUT_DUMP: AnchorInfo(EGRESS_OUT_DUMP, "EGRESS_SHAPE", 32, False),
    EGRESS_ENVELOPE_APPLY: AnchorInfo(EGRESS_ENVELOPE_APPLY, "EGRESS_SHAPE", 33, False),
    EGRESS_HEADERS_APPLY: AnchorInfo(EGRESS_HEADERS_APPLY, "EGRESS_SHAPE", 34, False),
    # EGRESS_FINALIZE (not persist-tied)
    EGRESS_HTTP_FINALIZE: AnchorInfo(
        EGRESS_HTTP_FINALIZE, "EGRESS_FINALIZE", 35, False
    ),
    EGRESS_TO_TRANSPORT_RESPONSE: AnchorInfo(
        EGRESS_TO_TRANSPORT_RESPONSE, "EGRESS_FINALIZE", 36, False
    ),
    # POST_RESPONSE (not persist-tied)
    EMIT_ALIASES_READ: AnchorInfo(EMIT_ALIASES_READ, "POST_RESPONSE", 37, False),
    OUT_DUMP: AnchorInfo(OUT_DUMP, "POST_RESPONSE", 38, False),
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
    "INGRESS_METHOD_EXTRACT",
    "INGRESS_PATH_EXTRACT",
    "INGRESS_HEADERS_PARSE",
    "INGRESS_QUERY_PARSE",
    "INGRESS_BODY_READ",
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
    "RESOLVE_VALUES",
    "PRE_FLUSH",
    "EMIT_ALIASES_PRE",
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
