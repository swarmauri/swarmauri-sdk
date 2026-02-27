from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Sequence


def build_router_and_attach(
    model: type,
    specs: Sequence[OpSpec],
    *,
    router: Any | None = None,
    only_keys: set[str] | None = None,
) -> None:
    del only_keys
    model_router = _build_router(model, specs, router=router)

    rest_ns = getattr(model, "rest", None)
    if rest_ns is None:
        rest_ns = SimpleNamespace()
        setattr(model, "rest", rest_ns)

    rest_ns.router = model_router
