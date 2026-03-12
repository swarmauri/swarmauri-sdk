"""Runtime event anchors and phase ordering helpers."""

from __future__ import annotations

PHASES = (
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

INGRESS_BEGIN = "INGRESS_BEGIN"
INGRESS_PARSE = "INGRESS_PARSE"
INGRESS_ROUTE = "INGRESS_ROUTE"

INGRESS_CTX_INIT = "ingress:ctx_init"
INGRESS_RAW_FROM_SCOPE = "ingress:raw_from_scope"
ROUTE_PROTOCOL_DETECT = "route:protocol_detect"
ROUTE_BINDING_MATCH = "route:match"
ROUTE_OP_RESOLVE = "route:op_resolve"
ROUTE_PLAN_SELECT = "route:plan_select"
ROUTE_CTX_FINALIZE = "route:ctx_finalize"

DEP_SECURITY = "dep:security"
DEP_EXTRA = "dep:extra"
SCHEMA_COLLECT_IN = "schema:collect_in"
RESOLVE_VALUES = "resolve:values"
OUT_BUILD = "out:build"
OUT_DUMP = "out:dump"

_EVENT_ORDER = (
    DEP_SECURITY,
    DEP_EXTRA,
    SCHEMA_COLLECT_IN,
    RESOLVE_VALUES,
    OUT_BUILD,
    OUT_DUMP,
)
_INDEX = {name: idx for idx, name in enumerate(_EVENT_ORDER)}


def order_events(anchors):
    return sorted(list(anchors or ()), key=lambda name: _INDEX.get(name, 10_000))


def prune_events_for_persist(anchors, *, persist: bool):
    anchors = list(anchors or ())
    if persist:
        return anchors
    persist_only = {RESOLVE_VALUES, DEP_SECURITY, DEP_EXTRA}
    return [anchor for anchor in anchors if anchor not in persist_only]


def is_error_phase(name: str) -> bool:
    return str(name).startswith("ON_")


__all__ = [
    "PHASES",
    "DEP_SECURITY",
    "DEP_EXTRA",
    "SCHEMA_COLLECT_IN",
    "RESOLVE_VALUES",
    "OUT_BUILD",
    "OUT_DUMP",
    "order_events",
    "prune_events_for_persist",
    "is_error_phase",
]
