from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple

from ... import events as _ev
from . import render as _render
from . import negotiation as _neg
from . import templates as _tmpl

RunFn = Callable[[Optional[object], Any], None]


async def _template(obj: Optional[object], ctx: Any) -> None:
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    tmpl = getattr(resp_ns, "template", None)
    if not tmpl:
        return
    result = getattr(resp_ns, "result", None)
    context = result if isinstance(result, dict) else {"data": result}
    html = await _tmpl.render_template(
        name=tmpl.name,
        context=context,
        search_paths=tmpl.search_paths,
        package=tmpl.package,
        auto_reload=bool(tmpl.auto_reload),
        filters=tmpl.filters,
        globals_=tmpl.globals,
        request=req,
    )
    resp_ns.result = html
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = _render.ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        hints.media_type = "text/html"


def _negotiate(obj: Optional[object], ctx: Any) -> None:
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = _render.ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        accept = getattr(req, "headers", {}).get("accept", "*/*")
        default_media = getattr(resp_ns, "default_media", "application/json")
        hints.media_type = _neg.negotiate_media_type(accept, default_media)


def _render_run(
    obj: Optional[object], ctx: Any
) -> None:  # pragma: no cover - glue code
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    result = getattr(resp_ns, "result", None)
    if result is None:
        return
    hints = getattr(resp_ns, "hints", None)
    default_media = getattr(resp_ns, "default_media", "application/json")
    envelope_default = getattr(resp_ns, "envelope_default", False)
    resp_ns.result = _render.render(
        req,
        result,
        hints=hints,
        default_media=default_media,
        envelope_default=envelope_default,
    )


REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("response", "template"): (_ev.OUT_DUMP, _template),
    ("response", "negotiate"): (_ev.OUT_DUMP, _negotiate),
    ("response", "render"): (_ev.OUT_DUMP, _render_run),
}


__all__ = ["REGISTRY", "RunFn"]
