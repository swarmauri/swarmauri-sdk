from __future__ import annotations

INGRESS_PHASES = ("INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE")
EGRESS_PHASES = ("EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE")
DEFAULT_PHASE_ORDER = (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "END_TX",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
)

LOWER_KIND_ASYNC_DIRECT = "async_direct"
LOWER_KIND_SYNC_EXTRACTABLE = "sync_extractable"
LOWER_KIND_SPLIT_EXTRACTABLE = "split_extractable"

EFFECT_NONE = -1
EFFECT_ROUTE_PROTOCOL_DETECT = 1
EFFECT_ROUTE_SELECTOR_RESOLVE = 2
EFFECT_ROUTE_PROGRAM_RESOLVE = 3
EFFECT_ROUTE_OP_RESOLVE = 4
EFFECT_INGRESS_METHOD_EXTRACT = 5
EFFECT_INGRESS_PATH_EXTRACT = 6
EFFECT_ROUTE_MATCH_REST = 7
EFFECT_ROUTE_MATCH_JSONRPC = 8
EFFECT_ROUTE_MATCH_WS = 9

EFFECT_BY_ATOM_NAME: dict[str, int] = {
    "route.protocol_detect": EFFECT_ROUTE_PROTOCOL_DETECT,
    "route.selector_resolve": EFFECT_ROUTE_SELECTOR_RESOLVE,
    "route.program_resolve": EFFECT_ROUTE_PROGRAM_RESOLVE,
    "route.op_resolve": EFFECT_ROUTE_OP_RESOLVE,
    "ingress.method_extract": EFFECT_INGRESS_METHOD_EXTRACT,
    "ingress.path_extract": EFFECT_INGRESS_PATH_EXTRACT,
    "route.match_rest": EFFECT_ROUTE_MATCH_REST,
    "route.match_jsonrpc": EFFECT_ROUTE_MATCH_JSONRPC,
    "route.match_ws": EFFECT_ROUTE_MATCH_WS,
}

ROUTE_SPINE_ATOMS = {
    "route.protocol_detect",
    "route.match_rest",
    "route.match_jsonrpc",
    "route.match_ws",
    "route.match_fallback",
    "route.selector_resolve",
    "route.program_resolve",
    "route.op_resolve",
}
