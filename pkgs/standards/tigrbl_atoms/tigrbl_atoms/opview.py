from __future__ import annotations
from types import SimpleNamespace
from typing import Any, Dict, Mapping


def _ensure_temp(ctx: Any) -> Dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def opview_from_ctx(ctx: Any):
    ov = getattr(ctx, "opview", None)
    if ov is not None:
        return ov
    try:
        from tigrbl_runtime.runtime import kernel as _kernel  # type: ignore
    except Exception:
        _kernel = None
    app = getattr(ctx, "app", None) or getattr(ctx, "router", None)
    model = getattr(ctx, "model", None) or (
        type(getattr(ctx, "obj", None))
        if getattr(ctx, "obj", None) is not None
        else None
    )
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if _kernel is not None and app and model and alias:
        return _kernel._default_kernel.get_opview(app, model, alias)
    if _kernel is not None and alias:
        specs = getattr(ctx, "specs", None)
        if specs is not None:
            return _kernel._default_kernel._compile_opview_from_specs(
                specs, SimpleNamespace(alias=alias)
            )
    raise RuntimeError("ctx_missing:opview")


def ensure_schema_in(ctx: Any, ov) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    if "schema_in" not in temp:
        bf = ov.schema_in.by_field
        req = tuple(n for n, e in bf.items() if e.get("required"))
        temp["schema_in"] = {
            "fields": ov.schema_in.fields,
            "by_field": bf,
            "required": req,
        }
    return temp["schema_in"]


def ensure_schema_out(ctx: Any, ov) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    if "schema_out" not in temp:
        temp["schema_out"] = {
            "fields": ov.schema_out.fields,
            "by_field": ov.schema_out.by_field,
            "expose": ov.schema_out.expose,
        }
    return temp["schema_out"]
