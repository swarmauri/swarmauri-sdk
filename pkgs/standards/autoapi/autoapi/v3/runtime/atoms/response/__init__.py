from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from .template import run as _template
from .negotiate import run as _negotiate
from .render import run as _render

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("response", "template"): (_ev.OUT_DUMP, _template),
    ("response", "negotiate"): (_ev.OUT_DUMP, _negotiate),
    ("response", "render"): (_ev.OUT_DUMP, _render),
}

__all__ = ["REGISTRY", "RunFn"]
