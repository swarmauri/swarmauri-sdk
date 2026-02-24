from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import attach_compiled as _attach_compiled
from . import body_peek as _body_peek
from . import body_read as _body_read
from . import ctx_init as _ctx_init
from . import headers_parse as _headers_parse
from . import method_extract as _method_extract
from . import path_extract as _path_extract
from . import query_parse as _query_parse

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("ingress", "ctx_init"): (_ctx_init.ANCHOR, _ctx_init.run),
    ("ingress", "attach_compiled"): (_attach_compiled.ANCHOR, _attach_compiled.run),
    ("ingress", "method_extract"): (_method_extract.ANCHOR, _method_extract.run),
    ("ingress", "path_extract"): (_path_extract.ANCHOR, _path_extract.run),
    ("ingress", "headers_parse"): (_headers_parse.ANCHOR, _headers_parse.run),
    ("ingress", "query_parse"): (_query_parse.ANCHOR, _query_parse.run),
    ("ingress", "body_read"): (_body_read.ANCHOR, _body_read.run),
    ("ingress", "body_peek"): (_body_peek.ANCHOR, _body_peek.run),
}

__all__ = ["REGISTRY", "RunFn"]
