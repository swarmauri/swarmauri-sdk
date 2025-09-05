from __future__ import annotations

from typing import Any, Callable, Optional

from ...runtime.kernel import build_phase_chains
from ._utils import Router, _label_hook
from .healthz import _build_healthz_endpoint
from .hookz import _build_hookz_endpoint
from .methodz import _build_methodz_endpoint
from .planz import _build_planz_endpoint


def mount_diagnostics(
    api: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
) -> Router:
    """
    Create & return a Router that exposes:
      GET /healthz
      GET /methodz
      GET /hookz
      GET /planz
    """
    router = Router()

    dep = get_db

    router.add_api_route(
        "/healthz",
        _build_healthz_endpoint(dep),
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
    )
    router.add_api_route(
        "/methodz",
        _build_methodz_endpoint(api),
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
    )
    router.add_api_route(
        "/hookz",
        _build_hookz_endpoint(api),
        methods=["GET"],
        name="hookz",
        tags=["system"],
        summary="Hooks",
        description=(
            "Expose hook execution order for each method.\n\n"
            "Phases appear in runner order; error phases trail.\n"
            "Within each phase, hooks are listed in execution order: "
            "global (None) hooks, then method-specific hooks."
        ),
    )
    router.add_api_route(
        "/planz",
        _build_planz_endpoint(api),
        methods=["GET"],
        name="planz",
        tags=["system"],
        summary="Plan",
        description="Flattened runtime execution plan per operation.",
    )

    return router


__all__ = [
    "mount_diagnostics",
    "_build_healthz_endpoint",
    "_build_methodz_endpoint",
    "_build_hookz_endpoint",
    "_build_planz_endpoint",
    "_label_hook",
    "build_phase_chains",
]
