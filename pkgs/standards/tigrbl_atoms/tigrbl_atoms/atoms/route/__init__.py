from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import ctx_finalize as _ctx_finalize
from . import jsonrpc_batch_intercept as _jsonrpc_batch_intercept
from . import match_fallback as _match_fallback
from . import match_jsonrpc as _match_jsonrpc
from . import match_rest as _match_rest
from . import match_ws as _match_ws
from . import op_resolve as _op_resolve
from . import params_normalize as _params_normalize
from . import payload_select as _payload_select
from . import protocol_detect as _protocol_detect
from . import rpc_envelope_parse as _rpc_envelope_parse

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("route", "protocol_detect"): (_protocol_detect.ANCHOR, _protocol_detect.INSTANCE),
    ("route", "rpc_envelope_parse"): (
        _rpc_envelope_parse.ANCHOR,
        _rpc_envelope_parse.INSTANCE,
    ),
    ("route", "match_jsonrpc"): (_match_jsonrpc.ANCHOR, _match_jsonrpc.INSTANCE),
    ("route", "match_rest"): (_match_rest.ANCHOR, _match_rest.INSTANCE),
    ("route", "match_ws"): (_match_ws.ANCHOR, _match_ws.INSTANCE),
    ("route", "match_fallback"): (_match_fallback.ANCHOR, _match_fallback.INSTANCE),
    ("route", "params_normalize"): (
        _params_normalize.ANCHOR,
        _params_normalize.INSTANCE,
    ),
    ("route", "payload_select"): (_payload_select.ANCHOR, _payload_select.INSTANCE),
    ("route", "op_resolve"): (_op_resolve.ANCHOR, _op_resolve.INSTANCE),
    ("route", "ctx_finalize"): (_ctx_finalize.ANCHOR, _ctx_finalize.INSTANCE),
    ("route", "jsonrpc_batch_intercept"): (
        _jsonrpc_batch_intercept.ANCHOR,
        _jsonrpc_batch_intercept.INSTANCE,
    ),
    # Legacy aliases kept while labels/plugins migrate.
    ("route", "binding_match"): (_match_rest.ANCHOR, _match_rest.INSTANCE),
    ("route", "rpc_method_match"): (_match_jsonrpc.ANCHOR, _match_jsonrpc.INSTANCE),
    ("route", "path_params_extract"): (
        _params_normalize.ANCHOR,
        _params_normalize.INSTANCE,
    ),
    ("route", "binding_policy_apply"): (
        _payload_select.ANCHOR,
        _payload_select.INSTANCE,
    ),
    ("route", "plan_select"): (_op_resolve.ANCHOR, _op_resolve.INSTANCE),
}

__all__ = ["REGISTRY", "RunFn"]
