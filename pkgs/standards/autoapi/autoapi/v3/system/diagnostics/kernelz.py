"""Diagnostic endpoint exposing kernel phase plans."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...op.types import PHASES


def build_kernelz_endpoint(api: Any):
    cache: Optional[Dict[str, Dict[str, Dict[str, List[str]]]]] = None

    async def _kernelz():
        nonlocal cache
        if cache is not None:
            return cache
        from . import _model_iter, _opspecs, _label_hook, build_phase_chains

        out: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            model_map: Dict[str, Dict[str, List[str]]] = {}
            for sp in _opspecs(model):
                chains = build_phase_chains(model, sp.alias)
                phase_map: Dict[str, List[str]] = {}
                for ph in PHASES:
                    steps = chains.get(ph, []) or []
                    if steps:
                        phase_map[ph] = [_label_hook(fn, ph) for fn in steps]
                model_map[sp.alias] = phase_map
            if model_map:
                out[mname] = model_map
        cache = out
        return out

    return _kernelz


__all__ = ["build_kernelz_endpoint"]
