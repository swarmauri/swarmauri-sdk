from __future__ import annotations

import logging
import threading
from types import SimpleNamespace
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple

from ...op.types import PHASES, StepFn
from ..executor import _Ctx, _invoke
from .. import events as _ev
from .atoms import (
    _DiscoveredAtom,
    _discover_atoms,
    _hook_phase_chains,
    _inject_atoms,
    _inject_pre_tx_dep_atoms,
    _inject_txn_system_steps,
    _is_persistent,
)
from .cache import _SpecsOnceCache, _WeakMaybeDict
from .models import OpView
from .opview_compiler import compile_opview_from_specs
from .payload import build_kernelz_payload

logger = logging.getLogger(__name__)


class Kernel:
    """
    SSoT for runtime scheduling. One Kernel per App (not per API).
    Auto-primed under the hood. Downstream users never touch this.
    """

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
        self._kernelz_payload = _WeakMaybeDict()
        self._primed = _WeakMaybeDict()
        self._lock = threading.Lock()

    def _atoms(self) -> list[_DiscoveredAtom]:
        if self._atoms_cache is None:
            self._atoms_cache = _discover_atoms()
        return self._atoms_cache

    def get_specs(self, model: type) -> Mapping[str, Any]:
        return self._specs_cache.get(model)

    def prime_specs(self, models: Sequence[type]) -> None:
        self._specs_cache.prime(models)

    def invalidate_specs(self, model: Optional[type] = None) -> None:
        self._specs_cache.invalidate(model)

    def build(self, model: type, alias: str) -> Dict[str, List[StepFn]]:
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
                _inject_txn_system_steps(chains)
            except Exception:
                logger.exception(
                    "kernel: failed to inject txn system steps for %s.%s",
                    getattr(model, "__name__", model),
                    alias,
                )
        for phase in PHASES:
            chains.setdefault(phase, [])
        return chains

    def plan_labels(self, model: type, alias: str) -> list[str]:
        labels: list[str] = []
        chains = self.build(model, alias)
        ordered_anchors = _ev.all_events_ordered()
        phase_for = {
            anchor: _ev.get_anchor_info(anchor).phase for anchor in ordered_anchors
        }
        for anchor in ordered_anchors:
            phase = phase_for[anchor]
            chain_phase = "PRE_TX_BEGIN" if phase == "PRE_TX" else phase
            for step in chains.get(chain_phase, []) or []:
                label = getattr(step, "__tigrbl_label", None)
                if isinstance(label, str) and label.endswith(f"@{anchor}"):
                    labels.append(label)
        return labels

    async def invoke(
        self,
        *,
        model: type,
        alias: str,
        db: Any,
        request: Any | None = None,
        ctx: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Execute an operation for ``model.alias`` using the executor."""
        phases = self.build(model, alias)
        base_ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        base_ctx.model = model
        base_ctx.op = alias
        specs = self.get_specs(model)
        base_ctx.opview = compile_opview_from_specs(specs, SimpleNamespace(alias=alias))
        return await _invoke(request=request, db=db, phases=phases, ctx=base_ctx)

    def ensure_primed(self, app: Any) -> None:
        """Autoprime once per App: specs → OpViews → /kernelz payload."""
        with self._lock:
            if self._primed.get(app):
                return
            from ...system.diagnostics.utils import (
                model_iter as _model_iter,
                opspecs as _opspecs,
            )

            models = list(_model_iter(app))
            for model in models:
                self._specs_cache.get(model)

            ov_map: Dict[Tuple[type, str], OpView] = {}
            for model in models:
                specs = self._specs_cache.get(model)
                for sp in _opspecs(model):
                    ov_map[(model, sp.alias)] = compile_opview_from_specs(specs, sp)
            self._opviews[app] = ov_map

            self._kernelz_payload[app] = build_kernelz_payload(self, app)
            self._primed[app] = True

    def get_opview(self, app: Any, model: type, alias: str) -> OpView:
        """Return OpView for (model, alias); compile on-demand if missing."""
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
            from ...system.diagnostics.utils import opspecs as _opspecs

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

    def kernelz_payload(self, app: Any) -> Dict[str, Dict[str, List[str]]]:
        """Thin accessor for endpoint: guarantees primed, returns cached payload."""
        self.ensure_primed(app)
        return self._kernelz_payload[app]

    def invalidate_kernelz_payload(self, app: Optional[Any] = None) -> None:
        with self._lock:
            if app is None:
                self._kernelz_payload = _WeakMaybeDict()
                self._opviews = _WeakMaybeDict()
                self._primed = _WeakMaybeDict()
            else:
                self._kernelz_payload.pop(app, None)
                self._opviews.pop(app, None)
                self._primed.pop(app, None)
