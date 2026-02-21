from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import extra as _extra
from . import security as _security

RunFn = Callable[[Optional[object], Any], Any]

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("dep", "security"): (_security.ANCHOR, _security.run),
    ("dep", "extra"): (_extra.ANCHOR, _extra.run),
}

__all__ = ["REGISTRY", "RunFn"]
