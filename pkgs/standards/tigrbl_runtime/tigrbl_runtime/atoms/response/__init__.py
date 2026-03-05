from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from .template import run as _template
from .negotiate import run as _negotiate
from .render import run as _render
from . import error_to_transport as _error_to_transport
from . import headers_from_payload as _hdr_payload

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("response", "template"): (_ev.OUT_DUMP, _template),
    ("response", "negotiate"): (_ev.OUT_DUMP, _negotiate),
    ("response", "headers_from_payload"): (_hdr_payload.ANCHOR, _hdr_payload.run),
    ("response", "render"): (_ev.OUT_DUMP, _render),
    ("response", "error_to_transport"): (
        _error_to_transport.ANCHOR,
        _error_to_transport.run,
    ),
}

__all__ = ["REGISTRY", "RunFn"]
