from __future__ import annotations

import logging
import re
import threading
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence

from tigrbl_runtime.hook_types import StepFn
from tigrbl_runtime.executor import _Ctx, _invoke
from . import events as _ev
from .atoms import (
    _DiscoveredAtom,
    _discover_atoms,
    _hook_phase_chains,
    _inject_atoms,
    _inject_pre_tx_dep_atoms,
    _inject_txn_system_steps,
    _is_persistent,
    _wrap_atom,
)
from .cache import _SpecsOnceCache, _WeakMaybeDict
from .models import CompiledPhase, KernelPlan, OpKey, OpMeta, OpView, PackedKernel
from .opview_compiler import compile_opview_from_specs

logger = logging.getLogger(__name__)


INGRESS_PHASES = ("INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE")
EGRESS_PHASES = ("EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE")
DEFAULT_PHASE_ORDER = tuple(getattr(_ev, "PHASES", ())) or (
    "INGRESS_BEGIN",
    "INGRESS_PARSE",
    "INGRESS_ROUTE",
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "END_TX",
    "POST_COMMIT",
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
)


def deepmerge_phase_chains(
    *phase_maps: Mapping[str, Sequence[StepFn]],
) -> Dict[str, List[StepFn]]:
    merged: Dict[str, List[StepFn]] = {}
    for phase_map in phase_maps:
        for phase, steps in (phase_map or {}).items():
            merged.setdefault(phase, []).extend(list(steps or ()))
    return {phase: list(steps) for phase, steps in merged.items()}


def _table_iter(app: Any) -> Sequence[Any]:
    tables = getattr(app, "tables", None)
    if isinstance(tables, dict):
        return tuple(v for v in tables.values() if isinstance(v, type))
    if isinstance(tables, Sequence) and not isinstance(tables, (str, bytes, bytearray)):
        return tuple(tables)
    return ()


def _opspecs(model: Any) -> Sequence[Any]:
    ops = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    if ops:
        return tuple(ops)

    table_ops = getattr(model, "ops", ()) or ()
    if table_ops:
        return tuple(table_ops)

    declared_ops = getattr(model, "__tigrbl_ops__", ()) or ()
    if declared_ops:
        return tuple(declared_ops)

    return ()


def _canonicalize_app(app: Any) -> Any:
    try:
        from tigrbl_core._spec.app_spec import AppSpec
        from tigrbl_canon.mapping.spec_normalization import normalize_app_spec
    except Exception:
        return app

    if isinstance(app, AppSpec):
        return normalize_app_spec(app)
    return app


def _label_callable(fn: Any) -> str:
    name = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    module = getattr(fn, "__module__", None)
    return f"{module}.{name}" if module else name


def _label_step(step: Any, phase: str) -> str:
    label = getattr(step, "__tigrbl_label", None)
    if isinstance(label, str) and "@" in label:
        return label
    module = getattr(step, "__module__", "") or ""
    name = getattr(step, "__name__", "") or ""
    if (
        module.startswith("tigrbl_ops_oltp.crud")
        or module.startswith("tigrbl_core.core.crud")
        and name
    ):
        return f"hook:wire:tigrbl:core:crud:ops:{name}@{phase}"
    return f"hook:wire:{_label_callable(step).replace('.', ':')}@{phase}"


def _compile_path_pattern(path: str) -> tuple[re.Pattern[str], tuple[str, ...]]:
    names: list[str] = []

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        names.append(name)
        return rf"(?P<{name}>[^/]+)"

    pattern = "^" + re.sub(r"\{([^{}]+)\}", _replace, path) + "$"
    return re.compile(pattern), tuple(names)


def _route_payload_template() -> dict[str, Any]:
    return {
        "http.rest": {"exact": {}, "templated": []},
        "https.rest": {"exact": {}, "templated": []},
        "http.jsonrpc": {},
        "https.jsonrpc": {},
        "ws": {"exact": {}, "templated": []},
        "wss": {"exact": {}, "templated": []},
    }


def _phase_info_map() -> tuple[dict[str, CompiledPhase], tuple[str, ...], tuple[str, ...]]:
    phases: dict[str, CompiledPhase] = {}
    if hasattr(_ev, "PHASES"):
        for name in DEFAULT_PHASE_ORDER:
            try:
                is_error = bool(getattr(_ev, "is_error_phase", lambda _n: False)(name))
            except Exception:
                is_error = False
            in_tx = name in {"START_TX", "PRE_HANDLER", "HANDLER", "END_TX", "POST_COMMIT"}
            phases[name] = CompiledPhase(
                name=name,
                stage_in=None,
                stage_out=None,
                in_tx=in_tx,
                is_error=is_error,
            )
    mainline = tuple(name for name in DEFAULT_PHASE_ORDER if not phases.get(name, CompiledPhase(name, None, None)).is_error)
    error = tuple(name for name in DEFAULT_PHASE_ORDER if phases.get(name, CompiledPhase(name, None, None)).is_error)
    return phases, mainline, error


class Kernel:
    _instance: ClassVar["Kernel | None"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Kernel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None):
        if atoms is None and getattr(self, "_singleton_initialized", False):
            self._reset(atoms)
            return
        self._reset(atoms)
        if atoms is None:
            self._singleton_initialized = True

    def _reset(self, atoms: Optional[Sequence[_DiscoveredAtom]] = None) -> None:
        self._atoms_cache = list(atoms) if atoms else None
        self._specs_cache = _SpecsOnceCache()
        self._opviews = _WeakMaybeDict()
        self._kernel_plans = _WeakMaybeDict()
        self._kernelz_payload = _WeakMaybeDict()
        self._primed = _WeakMaybeDict()
        self._lock = threading.Lock()

    def _atoms(self) -> list[_DiscoveredAtom]:
        if self._atoms_cache is None:
            self._atoms_cache = _discover_atoms()
        return self._atoms_cache

    def get_specs(self, model: type) -> Mapping[str, Any]:
        return self._specs_cache.get(model)

    def _compile_opview_from_specs(self, specs: Mapping[str, Any], sp: Any) -> OpView:
        return compile_opview_from_specs(specs, sp)

    def prime_specs(self, models: Sequence[type]) -> None:
        self._specs_cache.prime(models)

    def invalidate_specs(self, model: Optional[type] = None) -> None:
        self._specs_cache.invalidate(model)

    def build_op(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
        chains = _hook_phase_chains(model, alias)
        specs = getattr(getattr(model, "ops", SimpleNamespace()), "by_alias", {})
        sp_list = specs.get(alias) or ()
        sp = sp_list[0] if sp_list else None
        target = (getattr(sp, "target", alias) or "").lower()
        persist_policy = getattr(sp, "persist", "default")
        persistent = (
            persist_policy != "skip" and target not in {"read", "list"}
        ) or _is_persistent(chains)

        try:
            _inject_atoms(chains, self._atoms() or (), persistent=persistent)
        except Exception:
            logger.exception(
                "kernel: atom injection failed for %s.%s",
                getattr(model, "__name__", model),
                alias,
            )

        _inject_pre_tx_dep_atoms(chains, sp)

        if persistent:
            try:
                _inject_txn_system_steps(chains, model=model)
            except Exception:
                logger.exception(
                    "kernel: failed to inject txn system steps for %s.%s",
                    getattr(model, "__name__", model),
                    alias,
                )
        for phase in DEFAULT_PHASE_ORDER:
            chains.setdefault(phase, [])
        return chains

    def build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
        return self.build_op(model, alias)

    def build_ingress(self, app: Any) -> Dict[str, List[StepFn]]:
        del app
        order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
        ingress_atoms: Dict[str, List[tuple[str, Any]]] = {}
        for anchor, run in self._atoms() or ():
            if not _ev.is_valid_event(anchor):
                continue
            phase = _ev.phase_for_event(anchor)
            if phase not in INGRESS_PHASES:
                continue
            ingress_atoms.setdefault(phase, []).append((anchor, run))

        out: Dict[str, List[StepFn]] = {}
        for phase, atoms in ingress_atoms.items():
            ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
            out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
        return out

    def build_egress(self, app: Any) -> Dict[str, List[StepFn]]:
        del app
        order = {name: idx for idx, name in enumerate(_ev.all_events_ordered())}
        egress_atoms: Dict[str, List[tuple[str, Any]]] = {}
        for anchor, run in self._atoms() or ():
            if not _ev.is_valid_event(anchor):
                continue
            phase = _ev.phase_for_event(anchor)
            if phase not in EGRESS_PHASES:
                continue
            egress_atoms.setdefault(phase, []).append((anchor, run))

        out: Dict[str, List[StepFn]] = {}
        for phase, atoms in egress_atoms.items():
            ordered = sorted(atoms, key=lambda item: order.get(item[0], 10_000))
            out[phase] = [_wrap_atom(run, anchor=anchor) for anchor, run in ordered]
        return out

    def plan_labels(self, model: type, alias: str) -> list[str]:
        labels: list[str] = []
        chains = self.build(model, alias)
        opspec = next(
            (sp for sp in _opspecs(model) if getattr(sp, "alias", None) == alias),
            None,
        )
        persist = getattr(opspec, "persist", "default") != "skip"

        tx_begin = "START_TX:hook:sys:txn:begin@START_TX"
        tx_end = "END_TX:hook:sys:txn:commit@END_TX"
        if persist:
            labels.append(tx_begin)

        for phase in DEFAULT_PHASE_ORDER:
            if phase in {"START_TX", "END_TX"}:
                continue
            for step in chains.get(phase, ()) or ():
                labels.append(f"{phase}:{_label_step(step, phase)}")

        if persist:
            labels.append(tx_end)

        return labels

    def ensure_primed(self, app: Any) -> None:
        if self._primed.get(app):
            return
        with self._lock:
            if self._primed.get(app):
                return
            self.prime_specs(_table_iter(app))
            self._kernel_plans.pop(app, None)
            self._kernelz_payload.pop(app, None)
            self._opviews.pop(app, None)
            self._primed[app] = True

    def get_opview(self, app: Any, model: type, alias: str) -> OpView:
        ov_map = self._opviews.get(app)
        if isinstance(ov_map, dict):
            opview = ov_map.get((model, alias))
            if opview is not None:
                return opview

        self.ensure_primed(app)

        ov_map = self._opviews.setdefault(app, {})
        opview = ov_map.get((model, alias))
        if opview is not None:
            return opview

        try:
            specs = self._specs_cache.get(model)
            found = False
            for sp in _opspecs(model):
                ov_map.setdefault(
                    (model, sp.alias), compile_opview_from_specs(specs, sp)
                )
                if sp.alias == alias:
                    found = True

            if not found:
                temp_sp = SimpleNamespace(alias=alias)
                ov_map[(model, alias)] = compile_opview_from_specs(specs, temp_sp)

            return ov_map[(model, alias)]
        except Exception as exc:
            raise RuntimeError(
                f"opview_missing: app={app!r} model={getattr(model, '__name__', model)!r} alias={alias!r}"
            ) from exc

    async def _run_phase_chain(self, ctx: _Ctx, phases: Any) -> None:
        for _phase, steps in (phases or {}).items():
            for step in steps or ():
                rv = step(ctx)
                if hasattr(rv, "__await__"):
                    await rv

    async def _run_segment_python(self, ctx: _Ctx, packed: PackedKernel, seg_id: int) -> None:
        start = packed.segment_offsets[seg_id]
        end = start + packed.segment_lengths[seg_id]
        for idx in range(start, end):
            step_id = packed.segment_step_ids[idx]
            step = packed.step_table[step_id]
            rv = step(ctx)
            if hasattr(rv, "__await__"):
                await rv

    def _selector_from_ctx(self, ctx: _Ctx) -> tuple[str | None, str | None]:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return None, None

        proto = temp.get("proto") or temp.get("proto_name")
        selector = temp.get("selector") or temp.get("selector_name")

        if isinstance(proto, str) and isinstance(selector, str):
            return proto, selector

        route = temp.get("route")
        if isinstance(route, dict):
            route_proto = route.get("proto")
            route_selector = route.get("selector")
            if isinstance(route_proto, str) and isinstance(route_selector, str):
                return route_proto, route_selector

        proto_id = temp.get("proto_id")
        selector_id = temp.get("selector_id")
        packed = getattr(ctx, "kernel_plan", None)
        if isinstance(packed, KernelPlan) and packed.packed is not None:
            image = packed.packed
            if isinstance(proto_id, int) and 0 <= proto_id < len(image.proto_names):
                proto = image.proto_names[proto_id]
            if isinstance(selector_id, int) and 0 <= selector_id < len(image.selector_names):
                selector = image.selector_names[selector_id]
            if isinstance(proto, str) and isinstance(selector, str):
                return proto, selector

        return None, None

    def _resolve_program_id(self, ctx: _Ctx, packed: PackedKernel) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        proto_id = temp.get("proto_id")
        selector_id = temp.get("selector_id")
        if not isinstance(proto_id, int) or not isinstance(selector_id, int):
            proto_name, selector_name = self._selector_from_ctx(ctx)
            if isinstance(proto_name, str):
                proto_id = packed.proto_to_id.get(proto_name)
                if proto_id is not None:
                    temp["proto_id"] = proto_id
            if isinstance(selector_name, str):
                selector_id = packed.selector_to_id.get(selector_name)
                if selector_id is not None:
                    temp["selector_id"] = selector_id

        if not isinstance(proto_id, int) or not isinstance(selector_id, int):
            route = temp.get("route")
            if isinstance(route, dict):
                meta_index = route.get("opmeta_index")
                if isinstance(meta_index, int):
                    return meta_index
            return -1

        if proto_id < 0 or selector_id < 0:
            return -1
        if proto_id >= len(packed.route_to_program):
            return -1
        row = packed.route_to_program[proto_id]
        if selector_id >= len(row):
            return -1
        program_id = row[selector_id]
        return int(program_id) if isinstance(program_id, int) else -1

    async def _execute_packed(self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel) -> None:
        from tigrbl_canon.mapping.runtime_routes import invoke_runtime_route_handler
        from tigrbl_concrete.atoms.egress.asgi_send import _send_json, _send_transport_response
        from tigrbl_runtime.status import StatusDetailError, create_standardized_error

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        program_id = self._resolve_program_id(ctx, packed)
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
        opmeta = plan.opmeta[program_id]
        ctx.model = opmeta.model
        ctx.op = opmeta.alias
        ctx.opview = self.get_opview(app=ctx.app, model=opmeta.model, alias=opmeta.alias)

        seg_offset = packed.op_segment_offsets[program_id]
        seg_length = packed.op_segment_lengths[program_id]
        try:
            for i in range(seg_offset, seg_offset + seg_length):
                seg_id = packed.op_to_segment_ids[i]
                await self._run_segment_python(ctx, packed, seg_id)
        except StatusDetailError as exc:
            detail = exc.detail if getattr(exc, "detail", None) not in (None, "") else str(exc)
            await _send_json(env, int(getattr(exc, "status_code", 500) or 500), {"detail": detail})
            return
        except Exception as exc:
            std = create_standardized_error(exc)
            detail = std.detail if getattr(std, "detail", None) not in (None, "") else str(std)
            await _send_json(env, int(getattr(std, "status_code", 500) or 500), {"detail": detail})
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

    @staticmethod
    def _without_ingress_phases(phases: Mapping[str, Any] | None) -> dict[str, Any]:
        if not phases:
            return {}
        ingress = set(INGRESS_PHASES)
        return {phase: steps for phase, steps in phases.items() if phase not in ingress}

    def _segment_label(self, program_id: int, phase: str) -> str:
        return f"program:{program_id}:{phase}"

    def _build_route_matrix(
        self,
        *,
        proto_names: tuple[str, ...],
        selector_names: tuple[str, ...],
        opkey_to_meta: Mapping[OpKey, int],
    ) -> tuple[tuple[int, ...], ...]:
        proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
        selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
        matrix = [[-1 for _ in selector_names] for _ in proto_names]
        for key, meta_index in opkey_to_meta.items():
            proto_id = proto_to_id.get(key.proto)
            selector_id = selector_to_id.get(key.selector)
            if proto_id is None or selector_id is None:
                continue
            matrix[proto_id][selector_id] = int(meta_index)
        return tuple(tuple(row) for row in matrix)

    def _pack_kernel_plan(self, plan: KernelPlan) -> PackedKernel:
        selector_names = tuple(sorted({key.selector for key in plan.opkey_to_meta.keys()}))
        proto_names = tuple(sorted(plan.proto_indices.keys()))
        op_names = tuple(f"{meta.model.__name__}.{meta.alias}" for meta in plan.opmeta)

        proto_to_id = {name: idx for idx, name in enumerate(proto_names)}
        selector_to_id = {name: idx for idx, name in enumerate(selector_names)}
        op_to_id = {name: idx for idx, name in enumerate(op_names)}

        step_index: dict[int, int] = {}
        step_table: list[StepFn] = []
        step_labels: list[str] = []
        effect_ids: list[int] = []
        effect_payloads: list[tuple[int, ...]] = []

        segment_offsets: list[int] = []
        segment_lengths: list[int] = []
        segment_step_ids: list[int] = []
        segment_phases: list[str] = []
        segment_executor_kinds: list[str] = []

        op_segment_offsets: list[int] = []
        op_segment_lengths: list[int] = []
        op_to_segment_ids: list[int] = []

        for program_id, _meta in enumerate(plan.opmeta):
            chains = plan.phase_chains.get(program_id, {})
            op_segment_offsets.append(len(op_to_segment_ids))
            seg_count = 0
            for phase in DEFAULT_PHASE_ORDER:
                steps = list(chains.get(phase, ()) or ())
                if not steps:
                    continue

                seg_id = len(segment_offsets)
                segment_offsets.append(len(segment_step_ids))
                segment_lengths.append(len(steps))
                segment_phases.append(phase)
                segment_executor_kinds.append("python")

                for step in steps:
                    key = id(step)
                    step_id = step_index.get(key)
                    if step_id is None:
                        step_id = len(step_table)
                        step_index[key] = step_id
                        step_table.append(step)
                        step_labels.append(_label_step(step, phase))
                        effect = getattr(step, "__tigrbl_numba_effect__", None)
                        if isinstance(effect, tuple):
                            effect_id = int(effect[0]) if effect else -1
                            payload = tuple(int(v) for v in effect[1:])
                        elif isinstance(effect, int):
                            effect_id = int(effect)
                            payload = ()
                        else:
                            effect_id = -1
                            payload = ()
                        effect_ids.append(effect_id)
                        effect_payloads.append(payload)
                    segment_step_ids.append(step_id)

                op_to_segment_ids.append(seg_id)
                seg_count += 1
            op_segment_lengths.append(seg_count)

        route_to_program = self._build_route_matrix(
            proto_names=proto_names,
            selector_names=selector_names,
            opkey_to_meta=plan.opkey_to_meta,
        )

        packed = PackedKernel(
            proto_names=proto_names,
            selector_names=selector_names,
            op_names=op_names,
            proto_to_id=proto_to_id,
            selector_to_id=selector_to_id,
            op_to_id=op_to_id,
            route_to_program=route_to_program,
            segment_offsets=tuple(segment_offsets),
            segment_lengths=tuple(segment_lengths),
            segment_step_ids=tuple(segment_step_ids),
            segment_phases=tuple(segment_phases),
            segment_executor_kinds=tuple(segment_executor_kinds),
            op_segment_offsets=tuple(op_segment_offsets),
            op_segment_lengths=tuple(op_segment_lengths),
            op_to_segment_ids=tuple(op_to_segment_ids),
            step_table=tuple(step_table),
            step_labels=tuple(step_labels),
            numba_effect_ids=tuple(effect_ids),
            numba_effect_payloads=tuple(effect_payloads),
            executor_kind="python",
        )
        return replace(
            packed,
            executor=self._build_python_packed_executor(packed),
            numba_executor=self._build_numba_packed_executor(packed),
        )

    def _build_python_packed_executor(self, packed: PackedKernel):
        async def _executor(kernel: "Kernel", env: Any, ctx: _Ctx, plan: KernelPlan) -> None:
            await kernel._execute_packed(env, ctx, plan, packed)

        return _executor

    def _build_numba_packed_executor(self, packed: PackedKernel):
        if not packed.numba_effect_ids:
            return None
        if any(effect_id < 0 for effect_id in packed.numba_effect_ids):
            return None
        try:
            from numba import njit
        except Exception:
            return None

        route_to_program = packed.route_to_program
        op_segment_offsets = packed.op_segment_offsets
        op_segment_lengths = packed.op_segment_lengths
        op_to_segment_ids = packed.op_to_segment_ids
        segment_offsets = packed.segment_offsets
        segment_lengths = packed.segment_lengths
        segment_step_ids = packed.segment_step_ids
        effect_ids = packed.numba_effect_ids

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

        @njit(cache=True)
        def _program_checksum(program_id: int) -> int:
            if program_id < 0 or program_id >= len(op_segment_offsets):
                return -1
            acc = 0
            start = op_segment_offsets[program_id]
            end = start + op_segment_lengths[program_id]
            for idx in range(start, end):
                seg_id = op_to_segment_ids[idx]
                s = segment_offsets[seg_id]
                e = s + segment_lengths[seg_id]
                for j in range(s, e):
                    step_id = segment_step_ids[j]
                    acc += effect_ids[step_id]
            return acc

        def _executor(proto_id: int, selector_id: int) -> tuple[int, int]:
            program_id = int(_dispatch(int(proto_id), int(selector_id)))
            if program_id < 0:
                return -1, -1
            checksum = int(_program_checksum(program_id))
            return program_id, checksum

        return _executor

    async def handle_http(self, env: Any, app: Any) -> None:
        from tigrbl_canon.mapping.runtime_routes import invoke_runtime_route_handler
        from tigrbl_concrete.atoms.egress.asgi_send import (
            _send_json,
            _send_transport_response,
        )
        from tigrbl_runtime.status import StatusDetailError

        plan = self.kernel_plan(app)
        ctx = _Ctx.ensure(request=None, db=None)
        ctx.app = app
        ctx.router = app
        ctx.raw = env
        ctx.kernel_plan = plan

        if plan.packed is not None and plan.packed.executor is not None:
            await self._run_phase_chain(ctx, plan.ingress_chain)
            await plan.packed.executor(self, env, ctx, plan)
            return

        await self._run_phase_chain(ctx, plan.ingress_chain)

        route = (
            ctx.temp.get("route", {})
            if isinstance(getattr(ctx, "temp", None), dict)
            else {}
        )
        egress = (
            ctx.temp.get("egress", {})
            if isinstance(getattr(ctx, "temp", None), dict)
            else {}
        )
        if (
            isinstance(route, dict)
            and route.get("short_circuit") is True
            and isinstance(egress, dict)
            and egress.get("transport_response")
        ):
            await _send_transport_response(env, ctx)
            return

        opmeta_index = route.get("opmeta_index") if isinstance(route, dict) else None
        if not isinstance(opmeta_index, int):
            if isinstance(route, dict) and route.get("method_not_allowed") is True:
                await _send_json(env, 405, {"detail": "Method Not Allowed"})
                return
            handler = route.get("handler") if isinstance(route, dict) else None
            if callable(handler):
                await invoke_runtime_route_handler(ctx, handler=handler)
                await _send_transport_response(env, ctx)
                return
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        opmeta = plan.opmeta[opmeta_index]
        ctx.model = opmeta.model
        ctx.op = opmeta.alias
        ctx.opview = self.get_opview(app, opmeta.model, opmeta.alias)

        phases = self._without_ingress_phases(plan.phase_chains.get(opmeta_index, {}))
        try:
            await _invoke(request=None, db=None, phases=phases, ctx=ctx)
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
            from tigrbl_runtime.status import create_standardized_error

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

        await _send_transport_response(env, ctx)

    def compile_plan(self, app: Any) -> KernelPlan:
        app = _canonicalize_app(app)

        from tigrbl_core._spec.binding_spec import (
            HttpJsonRpcBindingSpec,
            HttpRestBindingSpec,
            WsBindingSpec,
        )

        route_data: dict[str, Any] = _route_payload_template()
        opmeta: list[OpMeta] = []
        opkey_to_meta: dict[OpKey, int] = {}
        phase_chains: dict[int, Mapping[str, list[StepFn]]] = {}
        ingress_chain = self.build_ingress(app)
        egress_chain = self.build_egress(app)
        phases, mainline_phases, error_phases = _phase_info_map()

        for model in _table_iter(app):
            for sp in _opspecs(model):
                meta_index = len(opmeta)
                target = (getattr(sp, "target", sp.alias) or sp.alias).lower()
                opmeta.append(OpMeta(model=model, alias=sp.alias, target=target))
                phase_chains[meta_index] = deepmerge_phase_chains(
                    ingress_chain,
                    self.build_op(model, sp.alias),
                    egress_chain,
                )

                for binding in getattr(sp, "bindings", ()) or ():
                    if isinstance(binding, HttpRestBindingSpec):
                        bucket = route_data.setdefault(
                            binding.proto, {"exact": {}, "templated": []}
                        )
                        for method in binding.methods:
                            selector = f"{method.upper()} {binding.path}"
                            opkey_to_meta[
                                OpKey(proto=binding.proto, selector=selector)
                            ] = meta_index
                            if "{" in binding.path and "}" in binding.path:
                                pattern, names = _compile_path_pattern(binding.path)
                                bucket["templated"].append(
                                    {
                                        "method": method.upper(),
                                        "path": binding.path,
                                        "pattern": pattern,
                                        "names": names,
                                        "meta_index": meta_index,
                                        "selector": selector,
                                    }
                                )
                            else:
                                bucket["exact"][selector] = meta_index

                    elif isinstance(binding, HttpJsonRpcBindingSpec):
                        opkey_to_meta[
                            OpKey(proto=binding.proto, selector=binding.rpc_method)
                        ] = meta_index
                        route_data.setdefault(binding.proto, {})[binding.rpc_method] = (
                            meta_index
                        )

                    elif isinstance(binding, WsBindingSpec):
                        bucket = route_data.setdefault(
                            binding.proto, {"exact": {}, "templated": []}
                        )
                        selector = binding.path
                        opkey_to_meta[OpKey(proto=binding.proto, selector=selector)] = (
                            meta_index
                        )

                        if "{" in binding.path and "}" in binding.path:
                            pattern, names = _compile_path_pattern(binding.path)
                            bucket["templated"].append(
                                {
                                    "path": binding.path,
                                    "pattern": pattern,
                                    "names": names,
                                    "meta_index": meta_index,
                                    "selector": selector,
                                    "subprotocols": tuple(binding.subprotocols or ()),
                                }
                            )
                        else:
                            bucket["exact"][selector] = meta_index

        semantic = KernelPlan(
            proto_indices=route_data,
            opmeta=tuple(opmeta),
            opkey_to_meta=opkey_to_meta,
            ingress_chain=ingress_chain,
            phase_chains=phase_chains,
            egress_chain=egress_chain,
            phases=phases,
            mainline_phases=mainline_phases,
            error_phases=error_phases,
        )
        return replace(semantic, packed=self._pack_kernel_plan(semantic))

    def compile_bootstrap_plan(self, app: Any) -> Dict[str, List[StepFn]]:
        return self.build_ingress(app)

    def kernel_plan(self, app: Any) -> KernelPlan:
        self.ensure_primed(app)
        plan = self._kernel_plans.get(app)
        if isinstance(plan, KernelPlan):
            return plan

        compiled = self.compile_plan(app)
        self._kernel_plans[app] = compiled

        payload: dict[str, dict[str, list[str]]] = {}
        for model in _table_iter(app):
            model_name = getattr(model, "__name__", str(model))
            payload[model_name] = {}
            for sp in _opspecs(model):
                payload[model_name][sp.alias] = self.plan_labels(model, sp.alias)
        self._kernelz_payload[app] = payload

        return compiled

    def kernelz_payload(self, app: Any) -> dict[str, dict[str, list[str]]]:
        self.kernel_plan(app)
        payload = self._kernelz_payload.get(app)
        if isinstance(payload, dict):
            return payload
        return {}

    def invalidate_kernelz_payload(self, app: Optional[Any] = None) -> None:
        with self._lock:
            if app is None:
                self._kernel_plans = _WeakMaybeDict()
                self._kernelz_payload = _WeakMaybeDict()
                self._opviews = _WeakMaybeDict()
                self._primed = _WeakMaybeDict()
            else:
                self._kernel_plans.pop(app, None)
                self._kernelz_payload.pop(app, None)
                self._opviews.pop(app, None)
                self._primed.pop(app, None)
