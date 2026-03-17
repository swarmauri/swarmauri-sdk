from __future__ import annotations

from collections.abc import Mapping
from typing import Any


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


def _normalize_schema_from_specs(ctx: Any) -> None:
    specs = getattr(ctx, "specs", None)
    op = getattr(ctx, "op", None)
    if not isinstance(specs, Mapping) or not isinstance(op, str) or not op:
        raise RuntimeError("ctx_missing:opview")

    in_fields: list[str] = []
    out_fields: list[str] = []
    by_field_in: dict[str, dict[str, Any]] = {}
    by_field_out: dict[str, dict[str, Any]] = {}

    for field_name, spec in specs.items():
        if not isinstance(field_name, str):
            continue
        io = getattr(spec, "io", None)
        fs = getattr(spec, "field", None)
        storage = getattr(spec, "storage", None)

        in_verbs = set(getattr(io, "in_verbs", ()) or ())
        out_verbs = set(getattr(io, "out_verbs", ()) or ())

        if op in in_verbs:
            in_fields.append(field_name)
            in_meta: dict[str, Any] = {"in_enabled": True}
            if storage is None:
                in_meta["virtual"] = True

            default_factory = getattr(spec, "default_factory", None)
            if callable(default_factory):
                in_meta["default_factory"] = default_factory

            alias_in = getattr(io, "alias_in", None)
            if alias_in:
                in_meta["alias_in"] = alias_in

            header_in = getattr(io, "header_in", None)
            if header_in:
                in_meta["header_in"] = header_in
                in_meta["header_required_in"] = bool(
                    getattr(io, "header_required_in", False)
                )

            in_meta["required"] = bool(fs and op in getattr(fs, "required_in", ()))
            in_meta["nullable"] = (
                True if storage is None else bool(getattr(storage, "nullable", True))
            )
            by_field_in[field_name] = in_meta

        if op in out_verbs:
            out_fields.append(field_name)
            out_meta: dict[str, Any] = {}

            alias_out = getattr(io, "alias_out", None)
            if alias_out:
                out_meta["alias_out"] = alias_out
            if storage is None:
                out_meta["virtual"] = True

            py_type = getattr(getattr(fs, "py_type", None), "__name__", None)
            if py_type:
                out_meta["py_type"] = py_type
            by_field_out[field_name] = out_meta

    in_fields_sorted = tuple(sorted(in_fields))
    out_fields_sorted = tuple(sorted(out_fields))

    setattr(
        ctx,
        "schema_in",
        {
            "fields": in_fields_sorted,
            "by_field": {f: by_field_in.get(f, {}) for f in in_fields_sorted},
            "required": tuple(
                f for f in in_fields_sorted if by_field_in.get(f, {}).get("required")
            ),
        },
    )
    setattr(
        ctx,
        "schema_out",
        {
            "fields": out_fields_sorted,
            "by_field": {f: by_field_out.get(f, {}) for f in out_fields_sorted},
            "expose": out_fields_sorted,
        },
    )


def _ensure_schema_in(ctx: Any) -> Mapping[str, Any]:
    temp = _ensure_temp(ctx)
    cached = temp.get("schema_in")
    if isinstance(cached, Mapping):
        return cached

    schema_in = getattr(ctx, "schema_in", None)
    if isinstance(schema_in, Mapping):
        temp["schema_in"] = schema_in
        return schema_in

    try:
        ov = _ensure_ov(ctx)
        bf = ov.schema_in.by_field
        req = tuple(n for n, e in bf.items() if e.get("required"))
        temp["schema_in"] = {
            "fields": ov.schema_in.fields,
            "by_field": bf,
            "required": req,
        }
    except RuntimeError as exc:
        if str(exc) != "ctx_missing:opview":
            raise
        _normalize_schema_from_specs(ctx)
        temp["schema_in"] = getattr(ctx, "schema_in")
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

    try:
        ov = _ensure_ov(ctx)
        temp["schema_out"] = {
            "fields": ov.schema_out.fields,
            "by_field": ov.schema_out.by_field,
            "expose": ov.schema_out.expose,
        }
    except RuntimeError as exc:
        if str(exc) != "ctx_missing:opview":
            raise
        _normalize_schema_from_specs(ctx)
        temp["schema_out"] = getattr(ctx, "schema_out")
    return temp["schema_out"]
