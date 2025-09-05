from __future__ import annotations

from typing import Any, Dict, List, Optional
from types import SimpleNamespace

from ...ops.types import PHASES
from ...runtime import plan as _plan


def build_planz_endpoint(api: Any):
    cache: Optional[Dict[str, Dict[str, List[str]]]] = None

    async def _planz():
        nonlocal cache
        """Expose the runtime step sequence for each operation."""
        if cache is not None:
            return cache
        from . import (
            _model_iter,
            _opspecs,
            _label_callable,
            _label_hook,
            build_phase_chains,
        )

        out: Dict[str, Dict[str, List[str]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            model_map: Dict[str, List[str]] = {}
            compiled_plan = getattr(
                getattr(model, "runtime", SimpleNamespace()), "plan", None
            )
            if compiled_plan is None:
                specs = getattr(model, "__autoapi_colspecs__", None) or getattr(
                    model, "__autoapi_cols__", None
                )
                if specs is not None:
                    try:
                        compiled_plan = _plan.attach_atoms_for_model(model, specs)
                    except Exception:
                        compiled_plan = None
            for sp in _opspecs(model):
                seq: List[str] = []
                persist = getattr(sp, "persist", "default") != "skip"
                if compiled_plan is not None:
                    deps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "deps", []) or []
                    ]
                    secdeps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "secdeps", []) or []
                    ]
                    hooks_root = getattr(model, "hooks", SimpleNamespace())
                    alias_ns = getattr(hooks_root, sp.alias, None)
                    hook_map: Dict[str, List[str]] = {}
                    if alias_ns is not None:
                        for ph in PHASES:
                            steps = getattr(alias_ns, ph, []) or []
                            if steps:
                                hook_map[ph] = [_label_hook(fn, ph) for fn in steps]
                    labels = _plan.flattened_order(
                        compiled_plan,
                        persist=persist,
                        include_system_steps=True,
                        deps=deps,
                        secdeps=secdeps,
                        hooks=hook_map,
                    )
                    labels = [
                        lbl
                        for lbl in labels
                        if not (
                            lbl.startswith("HANDLER:hook:")
                            and "hook:sys:handler:crud@HANDLER" not in lbl
                        )
                    ]
                    if sp.target == "custom" or getattr(sp, "persist", "default") in {
                        "override"
                    }:
                        labels = [
                            lbl
                            for lbl in labels
                            if "hook:sys:handler:crud@HANDLER" not in lbl
                        ]
                    seq = labels
                else:
                    deps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "deps", []) or []
                    ]
                    secdeps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "secdeps", []) or []
                    ]
                    chains = build_phase_chains(model, sp.alias)
                    seq.extend(f"PRE_TX:secdep:{s}" for s in secdeps)
                    seq.extend(f"PRE_TX:dep:{d}" for d in deps)
                    for ph in PHASES:
                        if ph == "PRE_TX":
                            continue
                        if ph == "START_TX" and persist:
                            seq.append("START_TX:hook:sys:txn:begin@START_TX")
                        if (
                            ph == "HANDLER"
                            and persist
                            and sp.target != "custom"
                            and getattr(sp, "persist", "default") not in {"override"}
                        ):
                            seq.append("HANDLER:hook:sys:handler:crud@HANDLER")
                        for step in chains.get(ph, []) or []:
                            name = getattr(step, "__name__", "")
                            if name in {"start_tx", "end_tx"}:
                                continue
                            seq.append(f"{ph}:{_label_hook(step, ph)}")
                        if ph == "END_TX" and persist:
                            seq.append("END_TX:hook:sys:txn:commit@END_TX")
                seen_wire = set()
                dedup_seq: List[str] = []
                for lbl in seq:
                    if lbl.startswith("hook:wire:"):
                        if lbl in seen_wire:
                            continue
                        seen_wire.add(lbl)
                    dedup_seq.append(lbl)
                model_map[sp.alias] = dedup_seq
            if model_map:
                out[mname] = model_map
        cache = out
        return cache

    return _planz
