from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_methodz_endpoint(api: Any):
    cache: Optional[Dict[str, List[Dict[str, Any]]]] = None

    async def _methodz():
        nonlocal cache
        """Ordered, canonical operation list."""
        if cache is not None:
            return cache

        from . import _model_iter, _opspecs

        methods: List[Dict[str, Any]] = []
        per_model: Dict[str, List[Dict[str, Any]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            for sp in _opspecs(model):
                if not getattr(sp, "expose_rpc", True):
                    continue
                entry = {
                    "method": f"{mname}.{sp.alias}",
                    "model": mname,
                    "alias": sp.alias,
                    "target": sp.target,
                    "arity": sp.arity,
                    "persist": sp.persist,
                    "request_model": getattr(sp, "request_model", None) is not None,
                    "response_model": getattr(sp, "response_model", None) is not None,
                    "routes": bool(getattr(sp, "expose_routes", True)),
                    "rpc": bool(getattr(sp, "expose_rpc", True)),
                    "tags": list(getattr(sp, "tags", ()) or (mname,)),
                }
                methods.append(entry)
                per_model.setdefault(mname, []).append(entry)
        methods.sort(key=lambda x: (x["model"], x["alias"]))
        cache = {"methods": methods, **per_model}
        return cache

    return _methodz
