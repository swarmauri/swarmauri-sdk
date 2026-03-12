from __future__ import annotations

from tigrbl_atoms import EGRESS_PHASES, INGRESS_PHASES, PHASE_SEQUENCE

LOWER_KIND_SYNC_EXTRACTABLE = "sync_extractable"
LOWER_KIND_SPLIT_EXTRACTABLE = "split_extractable"
LOWER_KIND_ASYNC_DIRECT = "async_direct"

# Canonical execution order fallback used by kernel compilation helpers.
DEFAULT_PHASE_ORDER = tuple(PHASE_SEQUENCE)

# Step effect metadata for optional compiler/runtime optimization hooks.
EFFECT_NONE = 0
EFFECT_DB_READ = 1
EFFECT_DB_WRITE = 2
EFFECT_WIRE = 3

EFFECT_BY_ATOM_NAME = {
    "sys.handler_read": EFFECT_DB_READ,
    "sys.handler_list": EFFECT_DB_READ,
    "sys.handler_create": EFFECT_DB_WRITE,
    "sys.handler_update": EFFECT_DB_WRITE,
    "sys.handler_replace": EFFECT_DB_WRITE,
    "sys.handler_merge": EFFECT_DB_WRITE,
    "sys.handler_delete": EFFECT_DB_WRITE,
    "sys.handler_bulk_create": EFFECT_DB_WRITE,
    "sys.handler_bulk_update": EFFECT_DB_WRITE,
    "sys.handler_bulk_replace": EFFECT_DB_WRITE,
    "sys.handler_bulk_merge": EFFECT_DB_WRITE,
    "sys.handler_bulk_delete": EFFECT_DB_WRITE,
    "egress.to_transport_response": EFFECT_WIRE,
    "egress.asgi_send": EFFECT_WIRE,
}

# Route atoms that can be lowered into fast sync extractors.
ROUTE_SPINE_ATOMS = {
    "route.protocol_detect",
    "route.match_rest",
    "route.match_jsonrpc",
    "route.match_ws",
    "route.match_fallback",
    "route.plan_select",
    "route.op_resolve",
    "route.program_resolve",
    "route.selector_resolve",
}

__all__ = [
    "DEFAULT_PHASE_ORDER",
    "INGRESS_PHASES",
    "EGRESS_PHASES",
    "EFFECT_NONE",
    "EFFECT_DB_READ",
    "EFFECT_DB_WRITE",
    "EFFECT_WIRE",
    "EFFECT_BY_ATOM_NAME",
    "ROUTE_SPINE_ATOMS",
    "LOWER_KIND_SYNC_EXTRACTABLE",
    "LOWER_KIND_SPLIT_EXTRACTABLE",
    "LOWER_KIND_ASYNC_DIRECT",
]
