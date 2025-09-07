from __future__ import annotations
from typing import Any, Mapping, Dict
from types import SimpleNamespace

from .kernel import _default_kernel as K  # single, app-scoped kernel


def _ensure_temp(ctx: Any) -> Dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def opview_from_ctx(ctx: Any):
    """
    Resolve the OpView for this request context, or raise a runtime error.
    Requirements:
      - ctx.app (or ctx.api), ctx.model (or derived from ctx.obj), ctx.op (or ctx.method)
    """
    app = getattr(ctx, "api", None) or getattr(ctx, "app", None)
    model = getattr(ctx, "model", None)
    if model is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            model = type(obj)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)

    if app and model and alias:
        # One-kernel-per-app, prime once; raises if not compiled
        return K.get_opview(app, model, alias)

    specs = getattr(ctx, "specs", None)
    if alias and specs is not None:
        return K._compile_opview_from_specs(specs, SimpleNamespace(alias=alias))

    missing = []
    if not alias:
        missing.append("op")
    if not app:
        missing.append("app")
    if not model:
        missing.append("model")
    # runtime-error policy: eject loudly; no skip
    raise RuntimeError(f"ctx_missing:{','.join(missing)}")


def ensure_schema_in(ctx: Any, ov) -> Mapping[str, Any]:
    """
    Load precompiled inbound schema from OpView into ctx.temp['schema_in'] if absent.
    """
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
    """
    Load precompiled outbound schema from OpView into ctx.temp['schema_out'] if absent.
    """
    temp = _ensure_temp(ctx)
    if "schema_out" not in temp:
        temp["schema_out"] = {
            "fields": ov.schema_out.fields,
            "by_field": ov.schema_out.by_field,
            "expose": ov.schema_out.expose,
        }
    return temp["schema_out"]


__all__ = ["opview_from_ctx", "ensure_schema_in", "ensure_schema_out", "_ensure_temp"]
