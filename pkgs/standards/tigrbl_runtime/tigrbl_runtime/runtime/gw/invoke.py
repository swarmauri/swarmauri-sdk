"""Compatibility gateway invoke entrypoint."""

from __future__ import annotations

from typing import Any

from tigrbl_runtime.runtime.runtime import Runtime

_runtime = Runtime()


async def invoke(env: Any, *, app: Any) -> Any:
    """Execute ASGI gateway requests against the runtime-owned kernel plan."""
    plan = _runtime.kernel.kernel_plan(app)
    packed_plan = getattr(plan, "packed", None)
    ctx: dict[str, Any] = {
        "app": app,
        "router": app,
        "raw": env,
        "temp": {},
    }
    executor = "packed" if packed_plan is not None else "phase"
    return await _runtime.invoke(
        executor=executor,
        env=env,
        ctx=ctx,
        plan=plan,
        packed_plan=packed_plan,
    )


__all__ = ["invoke"]
