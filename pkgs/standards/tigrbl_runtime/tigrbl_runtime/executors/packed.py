from __future__ import annotations

from typing import Any, ClassVar, Mapping
from types import SimpleNamespace

from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_kernel.models import KernelPlan, OpKey, PackedKernel

from .base import ExecutorBase
from .types import _Ctx


_PROGRAM_SEGMENT_CACHE: dict[
    int, dict[int, tuple[tuple[int, ...], dict[str, tuple[int, ...]]]]
] = {}


class PackedPlanExecutor(ExecutorBase):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    name: ClassVar[str] = "packed"
    _PHASE_EXECUTION_ORDER: ClassVar[tuple[str, ...]] = (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_DISPATCH",
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "END_TX",
        "POST_COMMIT",
        "POST_RESPONSE",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
    )

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

    def _resolve_program_id_from_dispatch(self, ctx: _Ctx, packed: PackedKernel) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        dispatch = temp.get("dispatch")
        if not isinstance(dispatch, dict):
            return -1

        selector = dispatch.get("binding_selector")
        protocol = dispatch.get("binding_protocol")
        if not (isinstance(selector, str) and isinstance(protocol, str)):
            return -1

        selector_to_id = getattr(packed, "selector_to_id", None)
        proto_to_id = getattr(packed, "proto_to_id", None)
        route_to_program = getattr(packed, "route_to_program", None)
        if not (
            isinstance(selector_to_id, Mapping)
            and isinstance(proto_to_id, Mapping)
            and route_to_program is not None
        ):
            return -1

        selector_id = self._coerce_int(selector_to_id.get(selector))
        proto_id = self._coerce_int(proto_to_id.get(protocol))
        if selector_id is None or proto_id is None:
            return -1
        if not (0 <= proto_id < len(route_to_program)):
            return -1

        row = route_to_program[proto_id]
        if not (0 <= selector_id < len(row)):
            return -1

        program_id = self._coerce_int(row[selector_id])
        if program_id is None or program_id < 0:
            return -1

        route = temp.setdefault("route", {})
        if isinstance(route, dict):
            route.setdefault("program_id", program_id)
            route.setdefault("opmeta_index", program_id)
        temp["program_id"] = program_id
        return program_id

    @staticmethod
    def _resolve_program_id_from_request(ctx: _Ctx, plan: KernelPlan) -> int:
        method = getattr(ctx, "method", None)
        path = getattr(ctx, "path", None)

        if not (isinstance(method, str) and isinstance(path, str) and path):
            raw = getattr(ctx, "raw", None)
            scope = getattr(raw, "scope", None) if raw is not None else None
            if isinstance(scope, Mapping):
                method = method or scope.get("method")
                path = path or scope.get("path")

        if not (isinstance(method, str) and isinstance(path, str) and path):
            return -1

        method = method.upper()
        selector = f"{method} {path}"
        for proto in ("http.rest", "https.rest"):
            maybe = plan.opkey_to_meta.get(OpKey(proto=proto, selector=selector))
            if isinstance(maybe, int):
                return maybe

        for proto in ("http.rest", "https.rest"):
            bucket = plan.proto_indices.get(proto)
            templated = bucket.get("templated") if isinstance(bucket, Mapping) else None
            if not isinstance(templated, list):
                continue
            for entry in templated:
                if not isinstance(entry, Mapping):
                    continue
                entry_method = str(entry.get("method", "") or "").upper()
                if entry_method and entry_method != method:
                    continue
                pattern = entry.get("pattern")
                if pattern is None or not hasattr(pattern, "match"):
                    continue
                if pattern.match(path) is None:
                    continue
                meta_index = entry.get("meta_index")
                if isinstance(meta_index, int):
                    return meta_index

        return -1

    async def _probe_ingress_for_program(
        self, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> int:
        if not getattr(plan, "opmeta", None):
            return -1

        seed_program_id = 0
        seg_offset = packed.op_segment_offsets[seed_program_id]
        seg_length = packed.op_segment_lengths[seed_program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = packed.op_to_segment_ids[i]
            phase = str(packed.segment_phases[seg_id])
            if not phase.startswith("INGRESS_"):
                break
            await self._run_segment_python(ctx, packed, seg_id)

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["ingress_probed"] = True

        program_id = self._require_program_id_from_ctx(ctx)
        if program_id < 0:
            program_id = self._resolve_program_id_from_dispatch(ctx, packed)
        if program_id < 0:
            program_id = self._resolve_program_id_from_request(ctx, plan)
        return program_id

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
            program_id = self._resolve_program_id_from_dispatch(ctx, packed)
        if program_id < 0:
            program_id = self._resolve_program_id_from_request(ctx, plan)
        if program_id < 0:
            program_id = await self._probe_ingress_for_program(ctx, plan, packed)
        if program_id < 0:
            egress = temp.get("egress") if isinstance(temp, dict) else None
            transport = (
                egress.get("transport_response") if isinstance(egress, dict) else None
            )
            if isinstance(transport, dict):
                await _send_transport_response(env, ctx)
                return

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

        meta = plan.opmeta[program_id]
        ctx.model = getattr(meta, "model", None)
        ctx.op = getattr(meta, "alias", None)
        ctx.target = getattr(meta, "target", None)
        env_ref = ctx.get("env")
        if env_ref is None:
            ctx["env"] = SimpleNamespace(method=ctx.op)
        elif getattr(env_ref, "method", None) in (None, "", "unknown"):
            try:
                setattr(env_ref, "method", ctx.op)
            except Exception:
                ctx["env"] = SimpleNamespace(method=ctx.op)
        release_db = None
        if getattr(ctx, "_raw_db", None) is None:
            try:
                db, release_db = _resolver.acquire(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=ctx.model,
                    op_alias=ctx.op if isinstance(ctx.op, str) else None,
                )
                ctx._raw_db = db
                ctx.owns_tx = True
            except Exception:
                release_db = None
        app = getattr(ctx, "app", None)
        if app is not None and ctx.model is not None and isinstance(ctx.op, str):
            ctx.opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)

        try:
            seg_offset = packed.op_segment_offsets[program_id]
            seg_length = packed.op_segment_lengths[program_id]
            packed_cache = _PROGRAM_SEGMENT_CACHE.setdefault(id(packed), {})
            cached = packed_cache.get(program_id)
            if cached is None:
                ordered_segments: list[int] = []
                by_phase_working: dict[str, list[int]] = {}
                remaining: list[int] = []
                seen_segment_ids: set[int] = set()
                for i in range(seg_offset, seg_offset + seg_length):
                    seg_id = packed.op_to_segment_ids[i]
                    phase = str(packed.segment_phases[seg_id])
                    by_phase_working.setdefault(phase, []).append(seg_id)

                for phase in self._PHASE_EXECUTION_ORDER:
                    for seg_id in by_phase_working.pop(phase, ()):  # pragma: no branch
                        if seg_id in seen_segment_ids:
                            continue
                        seen_segment_ids.add(seg_id)
                        ordered_segments.append(seg_id)

                for i in range(seg_offset, seg_offset + seg_length):
                    seg_id = packed.op_to_segment_ids[i]
                    if seg_id in seen_segment_ids:
                        continue
                    seen_segment_ids.add(seg_id)
                    remaining.append(seg_id)

                ordered = tuple((*ordered_segments, *remaining))
                by_phase = {
                    phase: tuple(segment_ids)
                    for phase, segment_ids in by_phase_working.items()
                }
                cached = (ordered, by_phase)
                packed_cache[program_id] = cached
            ordered, by_phase = cached

            try:
                for seg_id in ordered:
                    await self._run_segment_python(ctx, packed, seg_id)
            except StatusDetailError as exc:
                detail = (
                    exc.detail
                    if getattr(exc, "detail", None) not in (None, "")
                    else str(exc)
                )
                error_phase = f"ON_{getattr(ctx, 'phase', '')}_ERROR"
                fallback_phase = "ON_ERROR"
                for seg_id in (
                    *by_phase.get(error_phase, ()),
                    *by_phase.get(fallback_phase, ()),
                ):
                    try:
                        await self._run_segment_python(ctx, packed, seg_id)
                    except Exception:
                        pass
                await _send_json(
                    env,
                    int(getattr(exc, "status_code", 500) or 500),
                    {"detail": detail},
                )
                return
            except Exception as exc:
                std = create_standardized_error(exc)
                detail = (
                    std.detail
                    if getattr(std, "detail", None) not in (None, "")
                    else str(std)
                )
                error_phase = f"ON_{getattr(ctx, 'phase', '')}_ERROR"
                fallback_phase = "ON_ERROR"
                for seg_id in (
                    *by_phase.get(error_phase, ()),
                    *by_phase.get(fallback_phase, ()),
                ):
                    try:
                        await self._run_segment_python(ctx, packed, seg_id)
                    except Exception:
                        pass
                await _send_json(
                    env,
                    int(getattr(std, "status_code", 500) or 500),
                    {"detail": detail},
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
        finally:
            if callable(release_db):
                try:
                    release_db()
                except Exception:
                    pass

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
