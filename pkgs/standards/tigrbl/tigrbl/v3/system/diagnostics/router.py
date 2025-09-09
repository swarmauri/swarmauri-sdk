from __future__ import annotations

from typing import Any, Callable, Optional

from .compat import Router
from .healthz import build_healthz_endpoint
from .methodz import build_methodz_endpoint
from .hookz import build_hookz_endpoint
from .kernelz import build_kernelz_endpoint


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
      GET /kernelz
    """
    router = Router()

    dep = get_db

    router.add_api_route(
        "/healthz",
        build_healthz_endpoint(dep),
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
    )
    router.add_api_route(
        "/methodz",
        build_methodz_endpoint(api),
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
    )
    router.add_api_route(
        "/hookz",
        build_hookz_endpoint(api),
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
        "/kernelz",
        build_kernelz_endpoint(api),
        methods=["GET"],
        name="kernelz",
        tags=["system"],
        summary="Kernel Plan",
        description="Phase-chain plan as built by the kernel per operation.",
    )

    return router


__all__ = ["mount_diagnostics"]
