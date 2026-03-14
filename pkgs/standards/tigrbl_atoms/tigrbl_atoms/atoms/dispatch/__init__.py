from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import binding_match, binding_parse, input_normalize, op_resolve

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("dispatch", "binding_match"): (binding_match.ANCHOR, binding_match.INSTANCE),
    ("dispatch", "binding_parse"): (binding_parse.ANCHOR, binding_parse.INSTANCE),
    ("dispatch", "input_normalize"): (
        input_normalize.ANCHOR,
        input_normalize.INSTANCE,
    ),
    ("dispatch", "op_resolve"): (op_resolve.ANCHOR, op_resolve.INSTANCE),
}

__all__ = ["RunFn", "REGISTRY"]
