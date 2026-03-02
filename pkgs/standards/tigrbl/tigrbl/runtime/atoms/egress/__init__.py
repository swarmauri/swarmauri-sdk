from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from . import asgi_send as _asgi_send
from . import envelope_apply as _envelope_apply
from . import headers_apply as _headers_apply
from . import http_finalize as _http_finalize
from . import out_dump as _out_dump
from . import result_normalize as _result_normalize
from . import to_transport_response as _to_transport_response

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("egress", "result_normalize", _result_normalize.ANCHOR, _result_normalize.run),
    ("egress", "out_dump", _out_dump.ANCHOR, _out_dump.run),
    ("egress", "envelope_apply", _envelope_apply.ANCHOR, _envelope_apply.run),
    ("egress", "headers_apply", _headers_apply.ANCHOR, _headers_apply.run),
    ("egress", "http_finalize", _http_finalize.ANCHOR, _http_finalize.run),
    (
        "egress",
        "to_transport_response",
        _to_transport_response.ANCHOR,
        _to_transport_response.run,
    ),
    ("egress", "asgi_send", _asgi_send.ANCHOR, _asgi_send.run),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

_EVENT_ORDER = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
if tuple(REGISTRY):
    _anchors = [anchor for anchor, _run in REGISTRY.values()]
    if _anchors != sorted(_anchors, key=lambda a: _EVENT_ORDER.get(a, 10_000)):
        raise RuntimeError(
            "Egress atom registry order must follow runtime event order."
        )

__all__ = ["REGISTRY", "RunFn"]
