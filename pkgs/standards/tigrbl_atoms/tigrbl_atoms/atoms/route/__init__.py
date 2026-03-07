from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import binding_match as _binding_match
from . import binding_policy_apply as _binding_policy_apply
from . import ctx_finalize as _ctx_finalize
from . import jsonrpc_batch_intercept as _jsonrpc_batch_intercept
from . import op_resolve as _op_resolve
from . import params_normalize as _params_normalize
from . import path_params_extract as _path_params_extract
from . import payload_select as _payload_select
from . import plan_select as _plan_select
from . import protocol_detect as _protocol_detect
from . import rpc_envelope_parse as _rpc_envelope_parse
from . import rpc_method_match as _rpc_method_match

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("route", "protocol_detect"): (_protocol_detect.ANCHOR, _protocol_detect.INSTANCE),
    ("route", "binding_match"): (_binding_match.ANCHOR, _binding_match.INSTANCE),
    ("route", "rpc_envelope_parse"): (
        _rpc_envelope_parse.ANCHOR,
        _rpc_envelope_parse.INSTANCE,
    ),
    ("route", "rpc_method_match"): (
        _rpc_method_match.ANCHOR,
        _rpc_method_match.INSTANCE,
    ),
    ("route", "op_resolve"): (_op_resolve.ANCHOR, _op_resolve.INSTANCE),
    ("route", "path_params_extract"): (
        _path_params_extract.ANCHOR,
        _path_params_extract.INSTANCE,
    ),
    ("route", "params_normalize"): (
        _params_normalize.ANCHOR,
        _params_normalize.INSTANCE,
    ),
    ("route", "payload_select"): (_payload_select.ANCHOR, _payload_select.INSTANCE),
    ("route", "binding_policy_apply"): (
        _binding_policy_apply.ANCHOR,
        _binding_policy_apply.INSTANCE,
    ),
    ("route", "plan_select"): (_plan_select.ANCHOR, _plan_select.INSTANCE),
    ("route", "ctx_finalize"): (_ctx_finalize.ANCHOR, _ctx_finalize.INSTANCE),
    ("route", "jsonrpc_batch_intercept"): (
        _jsonrpc_batch_intercept.ANCHOR,
        _jsonrpc_batch_intercept.INSTANCE,
    ),
}

__all__ = ["REGISTRY", "RunFn"]
