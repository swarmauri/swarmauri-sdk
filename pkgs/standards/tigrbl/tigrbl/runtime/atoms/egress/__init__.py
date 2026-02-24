from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import envelope_apply as _envelope_apply
from . import headers_apply as _headers_apply
from . import http_finalize as _http_finalize
from . import out_dump as _out_dump
from . import result_normalize as _result_normalize
from . import to_transport_response as _to_transport_response

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("egress", "result_normalize"): (_result_normalize.ANCHOR, _result_normalize.run),
    ("egress", "out_dump"): (_out_dump.ANCHOR, _out_dump.run),
    ("egress", "envelope_apply"): (_envelope_apply.ANCHOR, _envelope_apply.run),
    ("egress", "headers_apply"): (_headers_apply.ANCHOR, _headers_apply.run),
    ("egress", "http_finalize"): (_http_finalize.ANCHOR, _http_finalize.run),
    ("egress", "to_transport_response"): (
        _to_transport_response.ANCHOR,
        _to_transport_response.run,
    ),
}

__all__ = ["REGISTRY", "RunFn"]
