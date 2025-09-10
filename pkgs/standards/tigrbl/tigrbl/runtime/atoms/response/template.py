from __future__ import annotations
from typing import Any, Optional

from ... import events as _ev
from .templates import render_template
from .renderer import ResponseHints

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
    hints = getattr(resp_ns, "hints", None)
    if hints is None:
        hints = ResponseHints()
        resp_ns.hints = hints
    if not hints.media_type:
        hints.media_type = "text/html"


__all__ = ["ANCHOR", "run"]
