from __future__ import annotations

from typing import Any, Mapping


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def opview_from_ctx(ctx: Any):
    ov = getattr(ctx, "opview", None)
    if ov is None:
        raise RuntimeError("ctx_missing:opview")
    return ov


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
