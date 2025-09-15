from __future__ import annotations

import inspect
from typing import Any, Mapping

try:  # align with pattern used in other REST helpers
    from fastapi import Header  # type: ignore
except Exception:  # pragma: no cover - fallback stub when FastAPI missing

    def Header(default=None, **kw):  # type: ignore
        return default


def _make_header_dep(model: type, alias: str):
    """
    Build a dependency that collects header values for fields declaring IO.header_in
    and exposes them as a mapping of canonical field name -> value.
    Only headers for verbs listed in IO.in_verbs for the current alias are considered.
    """

    # Collect (field, header_name) pairs honoring in_verbs
    hdr_fields: list[tuple[str, str]] = []
    try:
        for name, spec in getattr(model, "__tigrbl_cols__", {}).items():
            io = getattr(spec, "io", None)
            if not io:
                continue
            hname = getattr(io, "header_in", None)
            if not hname:
                continue
            in_verbs = set(getattr(io, "in_verbs", ()) or ())
            if alias not in in_verbs:
                continue
            hdr_fields.append((name, hname))
    except Exception:
        hdr_fields = []

    if not hdr_fields:

        async def _empty_dep() -> Mapping[str, Any]:  # pragma: no cover - trivial
            return {}

        _empty_dep.__name__ = f"headers_{model.__name__}_{alias}__empty"
        setattr(_empty_dep, "__tigrbl_has_headers__", False)
        return _empty_dep

    async def _dep(**kw: Any) -> Mapping[str, Any]:
        out: dict[str, Any] = {}
        for field, header in hdr_fields:
            param = header.lower().replace("-", "_")
            v = kw.get(param, None)
            if v is not None:
                out[field] = v
        return out

    # Build a signature with Header(...) params for FastAPI
    params: list[inspect.Parameter] = []
    seen: set[str] = set()
    for _field, header in hdr_fields:
        pname = header.lower().replace("-", "_")
        if pname in seen:
            continue  # avoid duplicate params if multiple fields read the same header
        seen.add(pname)
        params.append(
            inspect.Parameter(
                name=pname,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=Header(None),
                annotation=str | None,
            )
        )
    _dep.__signature__ = inspect.Signature(parameters=params, return_annotation=Mapping[str, Any])
    _dep.__name__ = f"headers_{model.__name__}_{alias}"
    setattr(_dep, "__tigrbl_has_headers__", True)
    return _dep


__all__ = ["_make_header_dep"]
