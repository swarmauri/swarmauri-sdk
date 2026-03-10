from __future__ import annotations

from typing import Any, Mapping


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _ensure_ov(ctx: Any):
    ov = getattr(ctx, "opview", None)
    if ov is None:
        raise RuntimeError("ctx_missing:opview")
    return ov


def _ensure_schema_in(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_in")
    if isinstance(cached, Mapping):
        return cached

    schema_in = getattr(ctx, "schema_in", None)
    if isinstance(schema_in, Mapping):
        temp["schema_in"] = schema_in
        return schema_in

    ov = _ensure_ov(ctx)
    bf = ov.schema_in.by_field
    req = tuple(n for n, e in bf.items() if e.get("required"))
    temp["schema_in"] = {
        "fields": ov.schema_in.fields,
        "by_field": bf,
        "required": req,
    }
    return temp["schema_in"]


def _ensure_schema_out(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_out")
    if isinstance(cached, Mapping):
        return cached

    schema_out = getattr(ctx, "schema_out", None)
    if isinstance(schema_out, Mapping):
        temp["schema_out"] = schema_out
        return schema_out

    ov = _ensure_ov(ctx)
    temp["schema_out"] = {
        "fields": ov.schema_out.fields,
        "by_field": ov.schema_out.by_field,
        "expose": ov.schema_out.expose,
    }
    return temp["schema_out"]
