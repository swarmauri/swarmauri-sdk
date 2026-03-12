from __future__ import annotations

from typing import Any, ClassVar, Mapping

from tigrbl_kernel.models import KernelPlan

from .base import ExecutorBase
from .types import _Ctx
from .invoke import _invoke


class PhaseExecutor(ExecutorBase):
    """Executes a kernel plan by running assembled phase chains."""

    name: ClassVar[str] = "phase"

    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        del env, packed_plan
        if not isinstance(plan, KernelPlan):
            raise TypeError("PhaseExecutor requires a KernelPlan instance")

        phases = runtime.kernel.build_phase_chains(plan)
        request = ctx.get("request") if isinstance(ctx, Mapping) else None
        db = ctx.get("db") if isinstance(ctx, Mapping) else None
        base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


__all__ = ["PhaseExecutor"]
