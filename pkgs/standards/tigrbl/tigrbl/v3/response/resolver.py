from __future__ import annotations
from typing import Dict, Optional

from dataclasses import fields
from .types import ResponseSpec, TemplateSpec
from ..runtime.atoms.response.renderer import ResponseHints


def _merge_template(
    base: Optional[TemplateSpec], over: Optional[TemplateSpec]
) -> Optional[TemplateSpec]:
    if over is None:
        return base
    if base is None:
        return over
    paths = list(base.search_paths)
    for p in over.search_paths:
        if p not in paths:
            paths.append(p)
    return TemplateSpec(
        name=over.name or base.name,
        search_paths=paths,
        package=over.package or base.package,
        auto_reload=over.auto_reload
        if over.auto_reload is not None
        else base.auto_reload,
        filters={**base.filters, **over.filters},
        globals={**base.globals, **over.globals},
    )


def _merge(
    base: Optional[ResponseSpec], over: Optional[ResponseSpec]
) -> Optional[ResponseSpec]:
    if over is None:
        return base
    if base is None:
        return over
    data = {f.name: getattr(base, f.name) for f in fields(base)}
    for f in fields(over):
        v = getattr(over, f.name)
        if v is not None:
            if f.name == "template":
                data[f.name] = _merge_template(getattr(base, f.name), v)
            elif isinstance(v, dict) and isinstance(data.get(f.name), dict):
                d = dict(data.get(f.name))
                d.update(v)
                data[f.name] = d
            else:
                data[f.name] = v
    return ResponseSpec(**data)


def resolve_response_spec(
    *candidates: Optional[ResponseSpec],
) -> Optional[ResponseSpec]:
    spec: Optional[ResponseSpec] = None
    for c in candidates:
        spec = _merge(spec, c)
    return spec


def infer_hints(
    spec: Optional[ResponseSpec],
) -> tuple[ResponseHints, Optional[bool], Optional[str]]:
    if spec is None:
        return ResponseHints(), None, None
    headers: Dict[str, str] = dict(spec.headers or {})
    if spec.cache_control:
        headers.setdefault("Cache-Control", spec.cache_control)
    hints = ResponseHints(
        media_type=spec.media_type,
        status_code=spec.status_code or 200,
        headers=headers,
        filename=spec.filename,
        download=bool(spec.download) if spec.download is not None else False,
        etag=spec.etag,
    )
    default_media = spec.media_type
    return hints, spec.envelope, default_media


__all__ = ["resolve_response_spec", "infer_hints"]
