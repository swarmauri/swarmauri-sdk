"""Concrete Tigrbl facades."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "TigrblApp": ".tigrbl_app",
    "TigrblRouter": ".tigrbl_router",
    "Template": ".response",
    "Response": ".._concrete._response",
    "JSONResponse": ".._concrete._json_response",
    "HTMLResponse": ".._concrete._html_response",
    "PlainTextResponse": ".._concrete._plain_text_response",
    "StreamingResponse": ".._concrete._streaming_response",
    "FileResponse": ".._concrete._file_response",
    "RedirectResponse": ".._concrete._redirect_response",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
