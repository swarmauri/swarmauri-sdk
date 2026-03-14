from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from . import ctx_init as _ctx_init
from . import input_prepare as _input_prepare
from . import transport_extract as _transport_extract

RunFn = Callable[[Optional[object], Any], Any]

_ORDERED: Tuple[Tuple[str, str, str, RunFn], ...] = (
    ("ingress", "ctx_init", _ctx_init.ANCHOR, _ctx_init.INSTANCE),
    (
        "ingress",
        "transport_extract",
        _transport_extract.ANCHOR,
        _transport_extract.INSTANCE,
    ),
    ("ingress", "input_prepare", _input_prepare.ANCHOR, _input_prepare.INSTANCE),
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
