from __future__ import annotations

from typing import Any, ClassVar, Mapping

from tigrbl_kernel.models import KernelPlan, PackedKernel

from .base import ExecutorBase
from .types import _Ctx


class PackedPlanExecutor(ExecutorBase):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    name: ClassVar[str] = "packed"

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        return value if isinstance(value, int) else None

    def _require_program_id_from_ctx(self, ctx: _Ctx) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        route = temp.get("route") if isinstance(temp, dict) else None
        if isinstance(route, dict):
            for key in ("program_id", "opmeta_index"):
                value = self._coerce_int(route.get(key))
                if value is not None:
                    temp["program_id"] = value
                    return value

        value = self._coerce_int(temp.get("program_id"))
        if value is not None:
            return value

        return -1

    async def _run_segment_python(
        self, ctx: _Ctx, packed: PackedKernel, seg_id: int
    ) -> None:
        ctx.phase = packed.segment_phases[seg_id]
        start = packed.segment_offsets[seg_id]
        end = start + packed.segment_lengths[seg_id]
        for idx in range(start, end):
            step_id = packed.segment_step_ids[idx]
            step = packed.step_table[step_id]
            rv = step(ctx)
            if hasattr(rv, "__await__"):
                await rv

    async def _execute_packed(
        self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> None:
        from tigrbl_atoms.atoms.egress.asgi_send import (
            _send_json,
            _send_transport_response,
        )
        from tigrbl_runtime.runtime.status import (
            StatusDetailError,
            create_standardized_error,
        )

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        program_id = self._require_program_id_from_ctx(ctx)
        if program_id < 0:
            route = temp.get("route", {})
            if isinstance(route, dict) and route.get("method_not_allowed") is True:
                await _send_json(env, 405, {"detail": "Method Not Allowed"})
                return
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        temp["program_id"] = program_id
        if program_id >= len(plan.opmeta):
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        seg_offset = packed.op_segment_offsets[program_id]
        seg_length = packed.op_segment_lengths[program_id]
        try:
            for i in range(seg_offset, seg_offset + seg_length):
                seg_id = packed.op_to_segment_ids[i]
                await self._run_segment_python(ctx, packed, seg_id)
        except StatusDetailError as exc:
            detail = (
                exc.detail
                if getattr(exc, "detail", None) not in (None, "")
                else str(exc)
            )
            await _send_json(
                env, int(getattr(exc, "status_code", 500) or 500), {"detail": detail}
            )
            return
        except Exception as exc:
            std = create_standardized_error(exc)
            detail = (
                std.detail
                if getattr(std, "detail", None) not in (None, "")
                else str(std)
            )
            await _send_json(
                env, int(getattr(std, "status_code", 500) or 500), {"detail": detail}
            )
            return

        route = temp.get("route", {}) if isinstance(temp, dict) else {}
        egress = temp.get("egress", {}) if isinstance(temp, dict) else {}
        if (
            isinstance(route, dict)
            and route.get("short_circuit") is True
            and isinstance(egress, dict)
            and egress.get("transport_response")
        ):
            await _send_transport_response(env, ctx)
            return

        await _send_transport_response(env, ctx)

    def _build_python_packed_executor(self, packed: PackedKernel):
        async def _executor(kernel: Any, env: Any, ctx: _Ctx, plan: KernelPlan) -> None:
            del kernel
            await self._execute_packed(env, ctx, plan, packed)

        return _executor

    def _build_numba_packed_executor(self, packed: PackedKernel):
        if not packed.route_to_program:
            return None
        try:
            from numba import njit
        except Exception:
            return None

        route_to_program = packed.route_to_program

        @njit(cache=True)
        def _dispatch(proto_id: int, selector_id: int) -> int:
            if proto_id < 0 or selector_id < 0:
                return -1
            if proto_id >= len(route_to_program):
                return -1
            row = route_to_program[proto_id]
            if selector_id >= len(row):
                return -1
            return row[selector_id]

        def _executor(proto_id: int, selector_id: int) -> int:
            return int(_dispatch(int(proto_id), int(selector_id)))

        return _executor

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
            request=ctx.get("request") if isinstance(ctx, Mapping) else None,
            db=ctx.get("db") if isinstance(ctx, Mapping) else None,
            seed=ctx,
        )
        await self._execute_packed(env, base_ctx, plan, packed_plan)
        return base_ctx.get("result")


__all__ = ["PackedPlanExecutor"]
