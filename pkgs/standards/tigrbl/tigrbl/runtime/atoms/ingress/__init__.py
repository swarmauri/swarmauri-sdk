from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from . import attach_compiled as _attach_compiled
from . import body_peek as _body_peek
from . import body_read as _body_read
from . import ctx_init as _ctx_init
from . import headers_parse as _headers_parse
from . import request_body_apply as _request_body_apply
from . import request_from_scope as _request_from_scope
from . import method_extract as _method_extract
from . import metrics_start as _metrics_start
from . import path_extract as _path_extract
from . import query_parse as _query_parse
from . import raw_from_scope as _raw_from_scope

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("ingress", "ctx_init", _ctx_init.ANCHOR, _ctx_init.run),
    ("ingress", "attach_compiled", _attach_compiled.ANCHOR, _attach_compiled.run),
    ("ingress", "metrics_start", _metrics_start.ANCHOR, _metrics_start.run),
    ("ingress", "raw_from_scope", _raw_from_scope.ANCHOR, _raw_from_scope.run),
    ("ingress", "method_extract", _method_extract.ANCHOR, _method_extract.run),
    ("ingress", "path_extract", _path_extract.ANCHOR, _path_extract.run),
    (
        "ingress",
        "request_from_scope",
        _request_from_scope.ANCHOR,
        _request_from_scope.run,
    ),
    ("ingress", "headers_parse", _headers_parse.ANCHOR, _headers_parse.run),
    ("ingress", "query_parse", _query_parse.ANCHOR, _query_parse.run),
    ("ingress", "body_read", _body_read.ANCHOR, _body_read.run),
    (
        "ingress",
        "request_body_apply",
        _request_body_apply.ANCHOR,
        _request_body_apply.run,
    ),
    ("ingress", "body_peek", _body_peek.ANCHOR, _body_peek.run),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

_EVENT_ORDER = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
if tuple(REGISTRY):
    _anchors = [anchor for anchor, _run in REGISTRY.values()]
    if _anchors != sorted(_anchors, key=lambda a: _EVENT_ORDER.get(a, 10_000)):
        raise RuntimeError(
            "Ingress atom registry order must follow runtime event order."
        )

__all__ = ["REGISTRY", "RunFn"]
