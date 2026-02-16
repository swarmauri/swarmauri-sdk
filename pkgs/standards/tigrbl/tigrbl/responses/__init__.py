from tigrbl.headers import Headers

from ._response import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)
from .decorators import (
    get_attached_response_alias,
    get_attached_response_spec,
    response_ctx,
)
from .resolver import infer_hints, resolve_response_spec
from .shortcuts import as_file, as_html, as_json, as_redirect, as_stream, as_text
from .types import Response as ResponseConfig
from .types import ResponseKind, ResponseSpec, Template, TemplateSpec
from ..runtime.atoms.response.renderer import ResponseHints, render
from ..runtime.atoms.response.templates import render_template

__all__ = [
    "Headers",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "FileResponse",
    "RedirectResponse",
    "response_ctx",
    "get_attached_response_spec",
    "get_attached_response_alias",
    "ResponseSpec",
    "ResponseKind",
    "TemplateSpec",
    "ResponseConfig",
    "Template",
    "resolve_response_spec",
    "infer_hints",
    "as_json",
    "as_html",
    "as_text",
    "as_redirect",
    "as_stream",
    "as_file",
    "ResponseHints",
    "render",
    "render_template",
]
