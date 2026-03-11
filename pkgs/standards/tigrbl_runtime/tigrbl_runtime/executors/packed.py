from __future__ import annotations

from typing import Any

from tigrbl_kernel.models import KernelPlan, PackedKernel

from .base import ExecutorBase
from .types import _Ctx


class PackedPlanExecutor(ExecutorBase):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    def __init__(self) -> None:
        super().__init__(name="packed")

    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        if not isinstance(plan, KernelPlan):
            raise TypeError("PackedPlanExecutor requires a KernelPlan instance")
        if not isinstance(packed_plan, PackedKernel):
            raise TypeError("PackedPlanExecutor requires a PackedKernel instance")

        base_ctx = _Ctx.ensure(
            request=ctx.get("request") if isinstance(ctx, dict) else None,
            db=ctx.get("db") if isinstance(ctx, dict) else None,
            seed=ctx,
        )
        await runtime.kernel._execute_packed(env, base_ctx, plan, packed_plan)
        return base_ctx.get("result")


__all__ = ["PackedPlanExecutor"]
