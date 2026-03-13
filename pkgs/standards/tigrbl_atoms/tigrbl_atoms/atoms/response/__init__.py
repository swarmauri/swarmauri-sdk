from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple

from . import template as _template
from . import negotiate as _negotiate
from . import render as _render
from . import error_to_transport as _error_to_transport
from . import headers_from_payload as _hdr_payload

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("response", "template"): (_template.ANCHOR, _template.INSTANCE),
    ("response", "negotiate"): (_negotiate.ANCHOR, _negotiate.INSTANCE),
    ("response", "headers_from_payload"): (_hdr_payload.ANCHOR, _hdr_payload.INSTANCE),
    ("response", "render"): (_render.ANCHOR, _render.INSTANCE),
    ("response", "error_to_transport"): (
        _error_to_transport.ANCHOR,
        _error_to_transport.INSTANCE,
    ),
}

__all__ = ["REGISTRY", "RunFn"]
