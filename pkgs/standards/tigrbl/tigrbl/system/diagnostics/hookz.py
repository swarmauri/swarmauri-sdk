from __future__ import annotations

from typing import Any, Dict, List, Optional
from types import SimpleNamespace

from ...op.types import PHASES


def build_hookz_endpoint(api: Any):
    cache: Optional[Dict[str, Dict[str, Dict[str, List[str]]]]] = None

    async def _hookz():
        nonlocal cache
        """
        Expose hook execution order for each method.

        Phases appear in runner order; error phases trail.
        Within each phase, hooks are listed in execution order: global (None) hooks,
        then method-specific hooks.
        """
        if cache is not None:
            return cache

        from . import _model_iter, _opspecs, _label_callable

        out: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            hooks_root = getattr(model, "hooks", SimpleNamespace())
            alias_sources = set()
            rpc_ns = getattr(model, "rpc", SimpleNamespace())
            alias_sources.update(getattr(rpc_ns, "__dict__", {}).keys())
            for sp in _opspecs(model):
                alias_sources.add(sp.alias)

            model_map: Dict[str, Dict[str, List[str]]] = {}
            for alias in sorted(alias_sources):
                alias_ns = getattr(hooks_root, alias, None) or SimpleNamespace()
                phase_map: Dict[str, List[str]] = {}
                for ph in PHASES:
                    steps = list(getattr(alias_ns, ph, []) or [])
                    if steps:
                        phase_map[ph] = [_label_callable(fn) for fn in steps]
                if phase_map:
                    model_map[alias] = phase_map
            out[mname] = model_map
        cache = out
        return cache

    return _hookz
