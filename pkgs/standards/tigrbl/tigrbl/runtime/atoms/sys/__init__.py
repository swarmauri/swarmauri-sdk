from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from . import commit_tx as _commit_tx
from . import handler_persistence as _handler_persistence
from . import runtime_route_handler as _runtime_route_handler
from . import start_tx as _start_tx

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("sys", "start_tx", _start_tx.ANCHOR, _start_tx.run),
    (
        "sys",
        "runtime_route_handler",
        _runtime_route_handler.ANCHOR,
        _runtime_route_handler.run,
    ),
    (
        "sys",
        "handler_persistence",
        _handler_persistence.ANCHOR,
        _handler_persistence.run,
    ),
    ("sys", "commit_tx", _commit_tx.ANCHOR, _commit_tx.run),
)

REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    (domain, subject): (anchor, run) for domain, subject, anchor, run in _ORDERED
}

__all__ = ["REGISTRY", "RunFn"]
