from __future__ import annotations

from typing import Any, ClassVar, Mapping
import json

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

    async def _resolve_program_id_fallback(
        self, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> int | None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        raw = getattr(ctx, "raw", None) or getattr(ctx, "env", None)
        scope = getattr(raw, "scope", None)
        if not isinstance(scope, dict):
            return None

        method = str(scope.get("method", "") or "").upper()
        path = str(scope.get("path", "/") or "/")
        rpc_method: str | None = None

        if scope.get("type") == "http":
            receive = getattr(raw, "receive", None)
            if callable(receive):
                chunks: list[bytes] = []
                while True:
                    message = await receive()
                    if (
                        not isinstance(message, dict)
                        or message.get("type") != "http.request"
                    ):
                        break
                    chunk = message.get("body", b"")
                    if isinstance(chunk, (bytes, bytearray)):
                        chunks.append(bytes(chunk))
                    if not bool(message.get("more_body", False)):
                        break
                if chunks:
                    body = b"".join(chunks)
                    ctx.body = body
                    ingress = temp.setdefault("ingress", {})
                    if isinstance(ingress, dict):
                        ingress["body"] = body
                        ingress["method"] = method
                        ingress["path"] = path
                    try:
                        payload = json.loads(body.decode("utf-8"))
                    except Exception:
                        payload = None
                    if isinstance(payload, Mapping):
                        temp.setdefault("dispatch", {})["body_json"] = dict(payload)
                        if isinstance(ingress, dict):
                            ingress["body_json"] = dict(payload)
                        if "params" in payload and isinstance(
                            payload.get("params"), Mapping
                        ):
                            ctx.payload = dict(payload.get("params") or {})
                        else:
                            ctx.payload = dict(payload)
                        maybe = payload.get("method")
                        if isinstance(maybe, str):
                            rpc_method = maybe

        proto_indices = getattr(plan, "proto_indices", {})
        if not isinstance(proto_indices, Mapping):
            return None

        matched_proto: str | None = None
        matched_selector: str | None = None
        for proto, bucket in proto_indices.items():
            if not isinstance(proto, str) or not isinstance(bucket, Mapping):
                continue
            if (
                proto.endswith(".jsonrpc")
                and isinstance(rpc_method, str)
                and rpc_method in bucket
            ):
                matched_proto = proto
                matched_selector = rpc_method
                break
            if proto.endswith(".rest"):
                selector = f"{method} {path}"
                exact = bucket.get("exact")
                if isinstance(exact, Mapping) and selector in exact:
                    matched_proto = proto
                    matched_selector = selector
                    break

        if matched_proto is None or matched_selector is None:
            return None

        proto_id = packed.proto_to_id.get(matched_proto)
        selector_id = packed.selector_to_id.get(matched_selector)
        if not isinstance(proto_id, int) or not isinstance(selector_id, int):
            return None
        if proto_id < 0 or proto_id >= len(packed.route_to_program):
            return None
        row = packed.route_to_program[proto_id]
        if selector_id < 0 or selector_id >= len(row):
            return None
        maybe = row[selector_id]
        if not isinstance(maybe, int) or maybe < 0:
            return None

        route = temp.setdefault("route", {})
        if isinstance(route, dict):
            route["program_id"] = maybe
            route["opmeta_index"] = maybe
            route["protocol"] = matched_proto
            route["selector"] = matched_selector
        return maybe

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
            resolved = await self._resolve_program_id_fallback(ctx, plan, packed)
            if isinstance(resolved, int):
                program_id = resolved
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

        meta = plan.opmeta[program_id]
        ctx.model = getattr(meta, "model", None)
        ctx.op = getattr(meta, "alias", None)
        ctx.target = getattr(meta, "target", None)
        app = getattr(ctx, "app", None)
        if app is not None and ctx.model is not None and isinstance(ctx.op, str):
            ctx.opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)

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
