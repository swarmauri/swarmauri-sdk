from __future__ import annotations

import logging
import threading
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, ClassVar, Mapping, Optional, Sequence

from tigrbl_runtime.hook_types import StepFn

from . import events as _ev
from ._build import (
    _build_route_matrix,
    _pack_kernel_plan,
    _segment_label,
    build,
    build_egress,
    build_ingress,
    build_op,
    compile_bootstrap_plan,
    plan_labels,
)
from ._executor import (
    _build_numba_packed_executor,
    _build_python_packed_executor,
    _coerce_int,
    _execute_packed,
    _require_program_id_from_ctx,
    _run_phase_chain,
    _run_segment_python,
)
from .atoms import _DiscoveredAtom, _discover_atoms
from .cache import _SpecsOnceCache, _WeakMaybeDict
from .models import KernelPlan, OpKey, OpMeta, OpView
from .opview_compiler import compile_opview_from_specs
from .types import DEFAULT_PHASE_ORDER as _DEFAULT_PHASE_ORDER
from .utils import (
    _canonicalize_app,
    _compile_path_pattern,
    _opspecs,
    _phase_info_map,
    _route_payload_template,
    _table_iter,
    deepmerge_phase_chains,
)

logger = logging.getLogger(__name__)


DEFAULT_PHASE_ORDER = tuple(getattr(_ev, "PHASES", ())) or _DEFAULT_PHASE_ORDER


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
        phases, mainline_phases, error_phases = _phase_info_map(DEFAULT_PHASE_ORDER)

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


Kernel.build_op = build_op
Kernel.build = build
Kernel.build_ingress = build_ingress
Kernel.build_egress = build_egress
Kernel.plan_labels = plan_labels
Kernel.compile_bootstrap_plan = compile_bootstrap_plan
Kernel._segment_label = _segment_label
Kernel._build_route_matrix = _build_route_matrix
Kernel._pack_kernel_plan = _pack_kernel_plan

Kernel._run_phase_chain = _run_phase_chain
Kernel._run_segment_python = _run_segment_python
Kernel._coerce_int = staticmethod(_coerce_int)
Kernel._require_program_id_from_ctx = _require_program_id_from_ctx
Kernel._execute_packed = _execute_packed
Kernel._build_python_packed_executor = _build_python_packed_executor
Kernel._build_numba_packed_executor = _build_numba_packed_executor
