from __future__ import annotations

import inspect
from typing import Mapping, Any

from fastapi import Header


def _build_signature_with_header_params(
    hdr_fields: list[tuple[str, str, bool]],
) -> inspect.Signature:
    params: list[inspect.Parameter] = []
    for _field, header, required in hdr_fields:
        param = header.lower().replace("-", "_")
        default = Header(... if required else None, alias=header)
        params.append(
            inspect.Parameter(
                name=param,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=str | None,
            )
        )
    return inspect.Signature(parameters=params, return_annotation=Mapping[str, object])


def _make_header_dep(model: type, alias: str):
    hdr_fields: list[tuple[str, str, bool]] = []
    for name, spec in getattr(model, "__tigrbl_cols__", {}).items():
        io = getattr(spec, "io", None)
        if not io or not getattr(io, "header_in", None):
            continue
        if alias not in set(getattr(io, "in_verbs", ()) or ()):  # honor IO.in_verbs
            continue
        hdr_fields.append(
            (name, io.header_in, bool(getattr(io, "header_required_in", False)))
        )

    async def _dep(**kw: Any) -> Mapping[str, object]:
        out: dict[str, object] = {}
        for field, header, _req in hdr_fields:
            param = header.lower().replace("-", "_")
            v = kw.get(param)
            if v is not None:
                out[field] = v
        return out

    _dep.__signature__ = _build_signature_with_header_params(hdr_fields)
    return _dep
