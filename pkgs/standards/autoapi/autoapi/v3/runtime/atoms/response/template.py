from __future__ import annotations
from typing import Any, Optional
import logging

from ... import events as _ev
from .templates import render_template
from .renderer import ResponseHints


logger = logging.getLogger("uvicorn")

ANCHOR = _ev.OUT_DUMP  # "out:dump"


async def run(obj: Optional[object], ctx: Any) -> None:
    """response:template@out:dump

    Render a template if configured on ``ctx.response``.
    """
    resp_ns = getattr(ctx, "response", None)
    req = getattr(ctx, "request", None)
    if resp_ns is None or req is None:
        return
    tmpl = getattr(resp_ns, "template", None)
    if not tmpl:
        return
    result = getattr(resp_ns, "result", None)
    logger.debug(
        "Template atom processing template %s with initial result type %s",
        getattr(tmpl, "name", None),
        type(result),
    )
    context = result if isinstance(result, dict) else {"data": result}
    html = await render_template(
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
    logger.debug(
        "Template atom produced HTML of length %d",
        len(html),
    )
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        hints.media_type = "text/html"
        logger.debug("Template atom set media_type to text/html")


__all__ = ["ANCHOR", "run"]
