from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import ctx_finalize, jsonrpc_batch_intercept, match_fallback, match_jsonrpc, match_rest, match_ws, op_resolve, params_normalize, payload_select, plan_select, program_resolve, protocol_detect, rpc_envelope_parse, selector_resolve

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("route", "protocol_detect"): (protocol_detect.ANCHOR, protocol_detect.INSTANCE),
    ("route", "rpc_envelope_parse"): (rpc_envelope_parse.ANCHOR, rpc_envelope_parse.INSTANCE),
    ("route", "match_jsonrpc"): (match_jsonrpc.ANCHOR, match_jsonrpc.INSTANCE),
    ("route", "match_rest"): (match_rest.ANCHOR, match_rest.INSTANCE),
    ("route", "match_ws"): (match_ws.ANCHOR, match_ws.INSTANCE),
    ("route", "match_fallback"): (match_fallback.ANCHOR, match_fallback.INSTANCE),
    ("route", "selector_resolve"): (selector_resolve.ANCHOR, selector_resolve.INSTANCE),
    ("route", "program_resolve"): (program_resolve.ANCHOR, program_resolve.INSTANCE),
    ("route", "params_normalize"): (params_normalize.ANCHOR, params_normalize.INSTANCE),
    ("route", "payload_select"): (payload_select.ANCHOR, payload_select.INSTANCE),
    ("route", "op_resolve"): (op_resolve.ANCHOR, op_resolve.INSTANCE),
    ("route", "ctx_finalize"): (ctx_finalize.ANCHOR, ctx_finalize.INSTANCE),
    ("route", "jsonrpc_batch_intercept"): (jsonrpc_batch_intercept.ANCHOR, jsonrpc_batch_intercept.INSTANCE),
    ("route", "plan_select"): (plan_select.ANCHOR, plan_select.INSTANCE),
}

__all__ = [
    "RunFn", "REGISTRY",
    "protocol_detect", "rpc_envelope_parse",
    "match_jsonrpc", "match_rest", "match_ws", "match_fallback",
    "selector_resolve", "program_resolve",
    "params_normalize", "payload_select", "op_resolve", "ctx_finalize",
    "jsonrpc_batch_intercept", "plan_select",
]
