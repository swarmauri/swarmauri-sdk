from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import extras as _extras
from . import security as _security

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("dep", "security"): (_security.ANCHOR, _security.run),
    ("dep", "extras"): (_extras.ANCHOR, _extras.run),
}

__all__ = ["REGISTRY", "RunFn"]
