from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple
from ....deps.starlette import Response
import logging

from ... import events as _ev
from . import render as _render_utils
from . import negotiation as _neg
from . import templates as _tmpl

RunFn = Callable[[Optional[object], Any], Any]

logger = logging.getLogger("uvicorn")


async def _template(obj: Optional[object], ctx: Any) -> None:
    logger.debug("Running response:template")
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
        hints = _render_utils.ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        hints.media_type = "text/html"


def _negotiate(obj: Optional[object], ctx: Any) -> None:
    logger.debug("Running response:negotiate")
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = _render_utils.ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        accept = getattr(req, "headers", {}).get("accept", "*/*")
        default_media = getattr(resp_ns, "default_media", "application/json")
        hints.media_type = _neg.negotiate_media_type(accept, default_media)


def _render(
    obj: Optional[object], ctx: Any
) -> Response | None:  # pragma: no cover - glue code
    """Render a payload into a concrete :class:`Response`.

    Returning the rendered ``Response`` allows the runtime executor to update
    ``ctx.result`` so later atoms or the final transport step don't overwrite
    the rendered output.
    """
    logger.debug("Running response:render")
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return None
    result = getattr(resp_ns, "result", None)
    if result is None:
        return None
    hints = getattr(resp_ns, "hints", None)
    default_media = getattr(resp_ns, "default_media", "application/json")
    envelope_default = getattr(resp_ns, "envelope_default", True)
    resp = _render_utils.render(
        req,
        result,
        hints=hints,
        default_media=default_media,
        envelope_default=envelope_default,
    )
    resp_ns.result = resp
    return resp


REGISTRY: Dict[Tuple[str, str], Tuple[str, RunFn]] = {
    ("response", "template"): (_ev.OUT_DUMP, _template),
    ("response", "negotiate"): (_ev.OUT_DUMP, _negotiate),
    ("response", "render"): (_ev.OUT_DUMP, _render),
}


__all__ = ["REGISTRY", "RunFn"]
