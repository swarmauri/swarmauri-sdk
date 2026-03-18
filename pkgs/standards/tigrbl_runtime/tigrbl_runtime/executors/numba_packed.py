from __future__ import annotations

from typing import Any, ClassVar

from tigrbl_kernel.models import KernelPlan, PackedKernel

from .packed import PackedPlanExecutor


class NumbaPackedPlanExecutor(PackedPlanExecutor):
    """Executes packed plans and prioritizes numba-compiled route dispatch."""

    name: ClassVar[str] = "numba_packed"

    def _resolve_program_id_from_dispatch(self, ctx: Any, packed: PackedKernel) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        dispatch = temp.get("dispatch")
        if not isinstance(dispatch, dict):
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        selector = dispatch.get("binding_selector")
        protocol = dispatch.get("binding_protocol")
        if not (isinstance(selector, str) and isinstance(protocol, str)):
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        selector_to_id = getattr(packed, "selector_to_id", None)
        proto_to_id = getattr(packed, "proto_to_id", None)
        numba_dispatch = getattr(packed, "numba_executor", None)
        if not callable(numba_dispatch):
            return super()._resolve_program_id_from_dispatch(ctx, packed)
        if not (hasattr(selector_to_id, "get") and hasattr(proto_to_id, "get")):
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        selector_id = self._coerce_int(selector_to_id.get(selector))
        proto_id = self._coerce_int(proto_to_id.get(protocol))
        if selector_id is None or proto_id is None:
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        try:
            program_id = int(numba_dispatch(proto_id, selector_id))
        except Exception:
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        if program_id < 0:
            return super()._resolve_program_id_from_dispatch(ctx, packed)

        route = temp.setdefault("route", {})
        if isinstance(route, dict):
            route.setdefault("program_id", program_id)
            route.setdefault("opmeta_index", program_id)
        temp["program_id"] = program_id
        return program_id

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
            raise TypeError("NumbaPackedPlanExecutor requires a KernelPlan instance")
        if not isinstance(packed_plan, PackedKernel):
            raise TypeError("NumbaPackedPlanExecutor requires a PackedKernel instance")
        return await super().invoke(
            runtime=runtime,
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )


__all__ = ["NumbaPackedPlanExecutor"]
