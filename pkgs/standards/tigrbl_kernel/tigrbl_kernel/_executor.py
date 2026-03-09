from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tigrbl_runtime.executor import _Ctx, _invoke

from .models import KernelPlan, PackedKernel

if TYPE_CHECKING:
    from .core import Kernel


async def _run(
    self,
    model: type,
    alias: str,
    *,
    db: Any,
    request: Any | None = None,
    ctx: Any | None = None,
) -> Any:
    phases = self._build_op(model, alias)
    base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)


async def _run_phase_chain(self, ctx: _Ctx, phases: Any) -> None:
    for _phase, steps in (phases or {}).items():
        for step in steps or ():
            rv = step(ctx)
            if hasattr(rv, "__await__"):
                await rv


async def _run_segment_python(
    self, ctx: _Ctx, packed: PackedKernel, seg_id: int
) -> None:
    start = packed.segment_offsets[seg_id]
    end = start + packed.segment_lengths[seg_id]
    for idx in range(start, end):
        step_id = packed.segment_step_ids[idx]
        step = packed.step_table[step_id]
        rv = step(ctx)
        if hasattr(rv, "__await__"):
            await rv


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


async def _execute_packed(
    self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
) -> None:
    from tigrbl_canon.mapping.runtime_routes import invoke_runtime_route_handler
    from tigrbl_concrete.atoms.egress.asgi_send import (
        _send_json,
        _send_transport_response,
    )
    from tigrbl_runtime.status import StatusDetailError, create_standardized_error

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
        handler = route.get("handler") if isinstance(route, dict) else None
        if callable(handler):
            await invoke_runtime_route_handler(ctx, handler=handler)
            await _send_transport_response(env, ctx)
            return
        await _send_json(env, 404, {"detail": "No runtime operation matched request."})
        return

    temp["program_id"] = program_id
    if program_id >= len(plan.opmeta):
        await _send_json(env, 404, {"detail": "No runtime operation matched request."})
        return

    seg_offset = packed.op_segment_offsets[program_id]
    seg_length = packed.op_segment_lengths[program_id]
    try:
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = packed.op_to_segment_ids[i]
            await self._run_segment_python(ctx, packed, seg_id)
    except StatusDetailError as exc:
        detail = (
            exc.detail if getattr(exc, "detail", None) not in (None, "") else str(exc)
        )
        await _send_json(
            env, int(getattr(exc, "status_code", 500) or 500), {"detail": detail}
        )
        return
    except Exception as exc:
        std = create_standardized_error(exc)
        detail = (
            std.detail if getattr(std, "detail", None) not in (None, "") else str(std)
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
    async def _executor(
        kernel: "Kernel", env: Any, ctx: _Ctx, plan: KernelPlan
    ) -> None:
        await kernel._execute_packed(env, ctx, plan, packed)

    return _executor


def _build_numba_packed_executor(self, packed: PackedKernel):
    """
    Numba target for an extracted synchronous route/program helper.

    Semantic route authority remains with route atoms. This helper is only an
    optional implementation detail for synchronous numeric dispatch extraction:

        program_id = route_to_program[proto_id, selector_id]
    """
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
