from __future__ import annotations

import logging
import re
import threading
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
from .models import KernelPlan, OpKey, OpMeta, OpView
from .labels import label_hook
from .opview_compiler import compile_opview_from_specs

logger = logging.getLogger(__name__)


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
        for phase in _ev.PHASES:
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
            if phase not in {"INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE"}:
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
            if phase not in {"EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}:
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

        for phase in _ev.PHASES:
            if phase in {
                "INGRESS_BEGIN",
                "INGRESS_PARSE",
                "INGRESS_ROUTE",
                "EGRESS_SHAPE",
                "EGRESS_FINALIZE",
                "START_TX",
                "END_TX",
            }:
                continue
            for step in chains.get(phase, ()) or ():
                labels.append(f"{phase}:{label_hook(step, phase)}")

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

    @staticmethod
    def _without_ingress_phases(phases: Mapping[str, Any] | None) -> dict[str, Any]:
        if not phases:
            return {}
        ingress = {"INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE"}
        return {phase: steps for phase, steps in phases.items() if phase not in ingress}

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

        return KernelPlan(
            proto_indices=route_data,  # compatibility field; now compiled route payload
            opmeta=tuple(opmeta),
            opkey_to_meta=opkey_to_meta,
            ingress_chain=ingress_chain,
            phase_chains=phase_chains,
            egress_chain=egress_chain,
        )

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
