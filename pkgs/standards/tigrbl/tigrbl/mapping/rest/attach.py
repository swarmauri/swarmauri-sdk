from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Sequence

from ...op import OpSpec
from .router import _build_router


def build_router_and_attach(
    model: type,
    specs: Sequence[OpSpec],
    *,
    router: Any | None = None,
    only_keys: set[tuple[str, str]] | None = None,
) -> Any:
    """
    Build a REST router for ``model`` and attach it to ``model.rest.router``.

    ``only_keys`` is accepted for compatibility with targeted rebind flows.
    For now we rebuild from the provided ``specs`` snapshot.
    """
    del only_keys
    model_router = _build_router(model, specs, router=router)
    rest_ns = getattr(model, "rest", None)
    if not isinstance(rest_ns, SimpleNamespace):
        rest_ns = SimpleNamespace()
    rest_ns.router = model_router
    setattr(model, "rest", rest_ns)
    return model_router
