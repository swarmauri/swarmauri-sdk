from __future__ import annotations

import asyncio
import inspect
from typing import Any, ClassVar, Mapping
from types import SimpleNamespace

from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_kernel.models import KernelPlan, OpKey, PackedKernel

from .base import ExecutorBase
from .types import _Ctx


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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._program_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]
        ] = {}
        self._request_program_cache: dict[tuple[int, str, str], int] = {}
        self._templated_route_cache: dict[int, tuple[tuple[str, Any, int], ...]] = {}
        self._opview_cache: dict[tuple[int, int], Any] = {}
        self._segment_steps_cache: dict[int, tuple[tuple[int, ...], ...]] = {}
        self._segment_runners_cache: dict[int, tuple[Any, ...]] = {}
        self._program_error_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], Mapping[str, tuple[int, ...]]]
        ] = {}
        self._program_runner_cache: dict[tuple[int, int], Any] = {}
        self._program_runner_mode_cache: dict[tuple[int, int, int], Any] = {}
        self._db_acquire_cache: dict[tuple[int, int], Any] = {}
        self._model_row_serializer_cache: dict[type[Any], tuple[str, ...]] = {}
        self._exact_route_entry_cache: dict[
            int, dict[tuple[str, str], tuple[int, bool, Any]]
        ] = {}
        self._program_meta_cache: dict[
            tuple[int, int], tuple[Any, Any, Any, Any | None, Any | None]
        ] = {}

    @classmethod
    def _resolve_transport_senders(cls):
        from tigrbl_atoms.atoms.egress.asgi_send import (
            _send_json,
            _send_transport_response,
        )

        return _send_json, _send_transport_response

    @classmethod
    def _resolve_error_helpers(cls):
        from tigrbl_runtime.runtime.status import (
            StatusDetailError,
            create_standardized_error,
        )

        return StatusDetailError, create_standardized_error

    def _resolve_segments_for_program(
        self, packed: PackedKernel, program_id: int
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_segments_cache.get(cache_key)
        if cached is not None:
            return cached

        seg_offset = packed.op_segment_offsets[program_id]
        seg_length = packed.op_segment_lengths[program_id]
        ordered_segments: list[int] = []
        by_phase: dict[str, list[int]] = {}
        remaining: list[int] = []
        seen_segment_ids: set[int] = set()
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = packed.op_to_segment_ids[i]
            phase = str(packed.segment_phases[seg_id])
            if phase.startswith("ON_"):
                continue
            by_phase.setdefault(phase, []).append(seg_id)

        for phase in self._PHASE_EXECUTION_ORDER:
            for seg_id in by_phase.pop(phase, ()):  # pragma: no branch
                if seg_id in seen_segment_ids:
                    continue
                seen_segment_ids.add(seg_id)
                ordered_segments.append(seg_id)

        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = packed.op_to_segment_ids[i]
            if seg_id in seen_segment_ids:
                continue
            phase = str(packed.segment_phases[seg_id])
            if phase.startswith("ON_"):
                continue
            seen_segment_ids.add(seg_id)
            remaining.append(seg_id)

        resolved = (tuple(ordered_segments), tuple(remaining))
        self._program_segments_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _coerce_model_column_keys(obj: Any) -> tuple[str, ...] | None:
        table = getattr(obj, "__table__", None)
        columns = getattr(table, "columns", None)
        if columns is None:
            return None
        out: list[str] = []
        for col in columns:
            key = getattr(col, "key", None)
            if isinstance(key, str) and key:
                out.append(key)
        return tuple(out)

    def _serialize_model_row(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, Mapping):
            return obj
        model_type = type(obj)
        keys = self._model_row_serializer_cache.get(model_type)
        if keys is None:
            keys = self._coerce_model_column_keys(obj)
            if keys is None:
                return obj
            self._model_row_serializer_cache[model_type] = keys
        if not keys:
            return obj
        return {key: getattr(obj, key, None) for key in keys}

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

    def _resolve_request_caches(
        self, plan: KernelPlan
    ) -> tuple[dict[tuple[int, str, str], int], tuple[tuple[str, Any, int], ...]]:
        plan_id = id(plan)
        templated = self._templated_route_cache.get(plan_id)
        if templated is None:
            exact: dict[tuple[int, str, str], int] = {}
            templated_routes: list[tuple[str, Any, int]] = []
            for proto in ("http.rest", "https.rest"):
                bucket = plan.proto_indices.get(proto)
                if not isinstance(bucket, Mapping):
                    continue
                exact_bucket = bucket.get("exact")
                if isinstance(exact_bucket, Mapping):
                    for selector, meta_index in exact_bucket.items():
                        if not (
                            isinstance(selector, str) and isinstance(meta_index, int)
                        ):
                            continue
                        method, _, path = selector.partition(" ")
                        if not path:
                            continue
                        exact[(plan_id, method.upper(), path)] = meta_index
                templated_bucket = bucket.get("templated")
                if isinstance(templated_bucket, list):
                    for entry in templated_bucket:
                        if not isinstance(entry, Mapping):
                            continue
                        meta_index = entry.get("meta_index")
                        pattern = entry.get("pattern")
                        if (
                            not isinstance(meta_index, int)
                            or pattern is None
                            or not hasattr(pattern, "match")
                        ):
                            continue
                        method = str(entry.get("method", "") or "").upper()
                        templated_routes.append((method, pattern, meta_index))
            self._request_program_cache.update(exact)
            templated = tuple(templated_routes)
            self._templated_route_cache[plan_id] = templated
        return self._request_program_cache, templated

    def _resolve_program_id_from_request(self, ctx: _Ctx, plan: KernelPlan) -> int:
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
        exact_cache, templated_routes = self._resolve_request_caches(plan)
        maybe = exact_cache.get((id(plan), method, path))
        if isinstance(maybe, int):
            return maybe

        selector = f"{method} {path}"
        for proto in ("http.rest", "https.rest"):
            maybe = plan.opkey_to_meta.get(OpKey(proto=proto, selector=selector))
            if isinstance(maybe, int):
                exact_cache[(id(plan), method, path)] = maybe
                return maybe

        for entry_method, pattern, meta_index in templated_routes:
            if entry_method and entry_method != method:
                continue
            if pattern.match(path) is None:
                continue
            exact_cache[(id(plan), method, path)] = meta_index
            return meta_index

        return -1

    def _resolve_compiled_exact_route_entries(
        self, packed: PackedKernel
    ) -> dict[tuple[str, str], tuple[int, bool, Any]]:
        packed_id = id(packed)
        cached = self._exact_route_entry_cache.get(packed_id)
        if cached is not None:
            return cached

        route_to_program = getattr(packed, "rest_exact_route_to_program", None)
        if not isinstance(route_to_program, Mapping):
            compiled: dict[tuple[str, str], tuple[int, bool, Any]] = {}
            self._exact_route_entry_cache[packed_id] = compiled
            return compiled

        hot_plans = tuple(getattr(packed, "hot_op_plans", ()) or ())
        compiled: dict[tuple[str, str], tuple[int, bool, Any]] = {}
        for route_key, program_id in route_to_program.items():
            if (
                not isinstance(route_key, tuple)
                or len(route_key) != 2
                or not isinstance(program_id, int)
                or program_id < 0
            ):
                continue
            method, path = route_key
            if not (isinstance(method, str) and isinstance(path, str)):
                continue
            hot_op_plan = hot_plans[program_id] if program_id < len(hot_plans) else None
            fast_direct_create = bool(
                hot_op_plan is not None
                and str(getattr(hot_op_plan, "target", "")).lower() == "create"
            )
            runner = self._resolve_program_runner_for_mode(
                packed,
                program_id,
                hot_op_plan,
                skip_dispatch=True,
                fast_direct_create=fast_direct_create,
            )
            compiled[(method.upper(), path)] = (program_id, fast_direct_create, runner)

        self._exact_route_entry_cache[packed_id] = compiled
        return compiled

    def _resolve_program_meta(
        self, plan: KernelPlan, packed: PackedKernel, program_id: int
    ) -> tuple[Any, Any, Any, Any | None, Any | None]:
        cache_key = (id(plan), program_id)
        cached = self._program_meta_cache.get(cache_key)
        if cached is not None:
            return cached

        hot_op_plan = (
            packed.hot_op_plans[program_id]
            if program_id < len(getattr(packed, "hot_op_plans", ()))
            else None
        )
        if hot_op_plan is not None:
            model = hot_op_plan.model
            alias = hot_op_plan.alias
            target = hot_op_plan.target
            opview = hot_op_plan.opview
        else:
            meta = plan.opmeta[program_id]
            model = getattr(meta, "model", None)
            alias = getattr(meta, "alias", None)
            target = getattr(meta, "target", None)
            opview = None

        resolved = (model, alias, target, opview, hot_op_plan)
        self._program_meta_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _resolve_program_id_from_exact_route(
        packed: PackedKernel, method: str, path: str
    ) -> int:
        route = getattr(packed, "rest_exact_route_to_program", None)
        if not isinstance(route, Mapping):
            return -1
        maybe = route.get((method.upper(), path))
        return maybe if isinstance(maybe, int) else -1

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
            await self._run_segment(ctx, packed, seg_id)

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["ingress_probed"] = True

        program_id = self._require_program_id_from_ctx(ctx)
        if (
            program_id < 0
            and isinstance(getattr(ctx, "method", None), str)
            and isinstance(getattr(ctx, "path", None), str)
        ):
            program_id = self._resolve_program_id_from_exact_route(
                packed, str(ctx.method), str(ctx.path)
            )
        if program_id < 0:
            program_id = self._resolve_program_id_from_dispatch(ctx, packed)
        if program_id < 0:
            program_id = self._resolve_program_id_from_request(ctx, plan)
        return program_id

    def _resolve_segment_step_ids(
        self, packed: PackedKernel
    ) -> tuple[tuple[int, ...], ...]:
        packed_id = id(packed)
        cached = self._segment_steps_cache.get(packed_id)
        if cached is not None:
            return cached
        compiled = []
        for segment_index in range(len(packed.segment_offsets)):
            start = packed.segment_offsets[segment_index]
            end = start + packed.segment_lengths[segment_index]
            compiled.append(
                tuple(packed.segment_step_ids[idx] for idx in range(start, end))
            )
        frozen = tuple(compiled)
        self._segment_steps_cache[packed_id] = frozen
        return frozen

    def _resolve_segment_runners(self, packed: PackedKernel) -> tuple[Any, ...]:
        packed_id = id(packed)
        cached = self._segment_runners_cache.get(packed_id)
        if cached is not None:
            return cached

        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(getattr(packed, "step_async_flags", ()) or ())
        executor_kinds = tuple(getattr(packed, "segment_executor_kinds", ()) or ())

        step_table = packed.step_table

        def _make_fused_sync_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    step(ctx)

            return _runner

        def _make_async_direct_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    await step(ctx)

            return _runner

        def _make_mixed_runner(step_ids: tuple[int, ...]):
            steps = tuple(
                (
                    step_table[step_id],
                    async_flags[step_id] if step_id < len(async_flags) else False,
                )
                for step_id in step_ids
            )

            async def _runner(ctx: _Ctx) -> None:
                for step, is_async in steps:
                    if is_async:
                        await step(ctx)
                        continue
                    rv = step(ctx)
                    if hasattr(rv, "__await__"):
                        await rv

            return _runner

        runners: list[Any] = []
        for seg_id, step_ids in enumerate(step_ids_by_segment):
            if (
                seg_id < len(executor_kinds)
                and executor_kinds[seg_id] == "sync.extractable"
            ):
                runners.append(_make_fused_sync_runner(step_ids))
            elif (
                seg_id < len(executor_kinds)
                and executor_kinds[seg_id] == "async.direct"
            ):
                runners.append(_make_async_direct_runner(step_ids))
            else:
                runners.append(_make_mixed_runner(step_ids))

        frozen = tuple(runners)
        self._segment_runners_cache[packed_id] = frozen
        return frozen

    def _resolve_program_runner(
        self, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> Any:
        cache_key = (id(packed), program_id)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached
        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = packed.segment_phases
        all_segment_ids = (*ordered, *remaining)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            skip_dispatch = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_exact_route")
            )
            fast_direct_create = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create")
            )
            for seg_id in all_segment_ids:
                phase_name = phase_names[seg_id]
                if skip_dispatch and phase_name in {
                    "INGRESS_BEGIN",
                    "INGRESS_DISPATCH",
                }:
                    continue
                if fast_direct_create and phase_name in {
                    "POST_COMMIT",
                    "EGRESS_SHAPE",
                    "EGRESS_FINALIZE",
                    "POST_RESPONSE",
                }:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner_for_mode(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
        *,
        skip_dispatch: bool = False,
        fast_direct_create: bool = False,
    ) -> Any:
        mode = (1 if skip_dispatch else 0) | (2 if fast_direct_create else 0)
        cache_key = (id(packed), program_id, mode)
        cached = self._program_runner_mode_cache.get(cache_key)
        if cached is not None:
            return cached

        base_runner = self._resolve_program_runner(packed, program_id, hot_op_plan)
        if not skip_dispatch and not fast_direct_create:
            self._program_runner_mode_cache[cache_key] = base_runner
            return base_runner

        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = packed.segment_phases
        all_segment_ids = (*ordered, *remaining)

        skip_phases = set()
        if skip_dispatch:
            skip_phases.update({"INGRESS_BEGIN", "INGRESS_DISPATCH"})
        if fast_direct_create:
            skip_phases.update(
                {"POST_COMMIT", "EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}
            )

        async def _runner(ctx: _Ctx) -> None:
            for seg_id in all_segment_ids:
                phase_name = phase_names[seg_id]
                if phase_name in skip_phases:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_mode_cache[cache_key] = _runner
        return _runner

    def _resolve_db_acquire(
        self,
        plan: KernelPlan,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(plan), program_id)
        cached = self._db_acquire_cache.get(cache_key)
        if cached is not None:
            return cached
        model = getattr(hot_op_plan, "model", None)
        alias = getattr(hot_op_plan, "alias", None)
        hint = str(getattr(hot_op_plan, "db_acquire_hint", "resolver") or "resolver")

        if hint == "model_get_db" and callable(
            getattr(model, "__tigrbl_get_db__", None)
        ):

            def _acquire(_ctx: _Ctx) -> tuple[Any, Any]:
                return _resolver.acquire(model=model)

            self._db_acquire_cache[cache_key] = _acquire
            return _acquire

        provider_cache: dict[str, Any] = {}

        def _release(db: Any) -> None:
            close = getattr(db, "close", None)
            if not callable(close):
                return
            try:
                rv = close()
                if inspect.isawaitable(rv):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(rv)
                    else:
                        loop.create_task(rv)
            except Exception:
                return

        def _acquire_from_provider(provider: Any) -> tuple[Any, Any]:
            db = provider.session()
            return db, lambda: _release(db)

        def _acquire(ctx: _Ctx) -> tuple[Any, Any]:
            provider = provider_cache.get("provider")
            if provider is not None:
                return _acquire_from_provider(provider)
            provider = _resolver.resolve_provider(
                router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                model=model,
                op_alias=alias if isinstance(alias, str) else None,
            )
            if provider is not None:
                provider_cache["provider"] = provider
                return _acquire_from_provider(provider)
            return _resolver.acquire(
                router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                model=model,
                op_alias=alias if isinstance(alias, str) else None,
            )

        self._db_acquire_cache[cache_key] = _acquire
        return _acquire

    async def _run_segment(self, ctx: _Ctx, packed: PackedKernel, seg_id: int) -> None:
        ctx.phase = packed.segment_phases[seg_id]
        await self._resolve_segment_runners(packed)[seg_id](ctx)

    def _resolve_error_segments(
        self,
        packed: PackedKernel,
        program_id: int,
    ) -> Mapping[str, tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_error_segments_cache.get(cache_key)
        if cached is not None:
            return cached[1]

        grouped: dict[str, list[int]] = {}
        seg_offset = packed.op_segment_offsets[program_id]
        seg_length = packed.op_segment_lengths[program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = packed.op_to_segment_ids[i]
            phase_name = str(packed.segment_phases[seg_id])
            if phase_name.startswith("ON_"):
                grouped.setdefault(phase_name, []).append(seg_id)

        ordered_segments, remaining_segments = self._resolve_segments_for_program(
            packed, program_id
        )
        frozen = {phase: tuple(seg_ids) for phase, seg_ids in grouped.items()}
        self._program_error_segments_cache[cache_key] = (
            (*ordered_segments, *remaining_segments),
            frozen,
        )
        return frozen

    async def _execute_packed(
        self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> None:
        _send_json, _send_transport_response = self._resolve_transport_senders()
        StatusDetailError, create_standardized_error = self._resolve_error_helpers()

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        method = getattr(ctx, "method", None)
        path = getattr(ctx, "path", None)
        exact_entry = None
        if isinstance(method, str) and isinstance(path, str):
            exact_entry = self._resolve_compiled_exact_route_entries(packed).get(
                (method.upper(), path)
            )

        program_id = self._require_program_id_from_ctx(ctx)
        resolved_from_exact_route = False
        if program_id < 0 and exact_entry is not None:
            program_id = exact_entry[0]
            resolved_from_exact_route = True
        elif program_id < 0 and isinstance(method, str) and isinstance(path, str):
            program_id = self._resolve_program_id_from_exact_route(packed, method, path)
            resolved_from_exact_route = program_id >= 0
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
        if resolved_from_exact_route:
            temp["_tigrbl_hot_exact_route"] = True

        if program_id >= len(plan.opmeta):
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return
        model, alias, target, hot_opview, hot_op_plan = self._resolve_program_meta(
            plan, packed, program_id
        )
        ctx.model = model
        ctx.op = alias
        ctx.target = target

        if (
            resolved_from_exact_route
            and exact_entry is not None
            and exact_entry[1] is True
        ):
            temp["_tigrbl_hot_direct_create"] = True
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
                acquire_db = self._resolve_db_acquire(plan, program_id, hot_op_plan)
                db, release_db = acquire_db(ctx)
                ctx._raw_db = db
                ctx.owns_tx = True
            except Exception:
                release_db = None
        if hot_opview is not None:
            ctx.opview = hot_opview
        else:
            app = getattr(ctx, "app", None)
            if app is not None and ctx.model is not None and isinstance(ctx.op, str):
                opview_key = (id(plan), program_id)
                opview = self._opview_cache.get(opview_key)
                if opview is None:
                    opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)
                    self._opview_cache[opview_key] = opview
                ctx.opview = opview

        try:
            if hot_op_plan is not None:
                error_phase_segments = hot_op_plan.error_segment_ids
            else:
                error_phase_segments = self._resolve_error_segments(
                    packed,
                    program_id,
                )

            try:
                if exact_entry is not None and resolved_from_exact_route:
                    await exact_entry[2](ctx)
                else:
                    await self._resolve_program_runner_for_mode(
                        packed,
                        program_id,
                        hot_op_plan,
                        skip_dispatch=resolved_from_exact_route,
                        fast_direct_create=bool(
                            isinstance(temp, dict)
                            and temp.get("_tigrbl_hot_direct_create") is True
                        ),
                    )(ctx)
            except StatusDetailError as exc:
                detail = (
                    exc.detail
                    if getattr(exc, "detail", None) not in (None, "")
                    else str(exc)
                )
                error_phase = f"ON_{getattr(ctx, 'phase', '')}_ERROR"
                fallback_phase = "ON_ERROR"
                for seg_id in (
                    *error_phase_segments.get(error_phase, ()),
                    *error_phase_segments.get(fallback_phase, ()),
                ):
                    try:
                        await self._run_segment(ctx, packed, seg_id)
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
                    *error_phase_segments.get(error_phase, ()),
                    *error_phase_segments.get(fallback_phase, ()),
                ):
                    try:
                        await self._run_segment(ctx, packed, seg_id)
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
            if isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create") is True:
                status = int(getattr(ctx, "status_code", 201) or 201)
                payload = self._serialize_model_row(getattr(ctx, "result", None))
                await _send_json(env, status, payload)
                return
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
