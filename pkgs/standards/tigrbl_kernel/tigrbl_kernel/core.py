from __future__ import annotations

import logging
import threading
from types import SimpleNamespace
from typing import Any, ClassVar, Mapping, Optional, Sequence


from . import events as _ev
from ._build import (
    _build_route_matrix,
    _pack_kernel_plan,
    _segment_label,
    _build,
    _build_egress,
    _build_ingress,
    _build_op,
    _compile_bootstrap_plan,
    _plan_labels,
)
from ._compile import _compile_opview_from_specs, _compile_plan
from .atoms import _DiscoveredAtom, _discover_atoms
from .cache import _SpecsOnceCache, _WeakMaybeDict
from .models import KernelPlan, OpView
from .opview_compiler import compile_opview_from_specs
from .types import DEFAULT_PHASE_ORDER as _DEFAULT_PHASE_ORDER
from .utils import (
    _opspecs,
    _table_iter,
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

    def plan_labels(self, model: type, alias: str) -> list[str]:
        return self._plan_labels(model, alias)

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
                payload[model_name][sp.alias] = self._plan_labels(model, sp.alias)
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


Kernel._build_op = _build_op
Kernel._build = _build
Kernel._build_ingress = _build_ingress
Kernel._build_egress = _build_egress
Kernel._plan_labels = _plan_labels
Kernel._compile_bootstrap_plan = _compile_bootstrap_plan
Kernel._segment_label = _segment_label
Kernel._build_route_matrix = _build_route_matrix
Kernel._pack_kernel_plan = _pack_kernel_plan

Kernel.compile_plan = _compile_plan
Kernel.compile_bootstrap_plan = _compile_bootstrap_plan
Kernel._compile_opview_from_specs = _compile_opview_from_specs
