"""Concrete generic class implementations for tigrbl."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "App": "_app",
    "Column": "_column",
    "Engine": "_engine",
    "FileResponse": "_response",
    "HTMLResponse": "_response",
    "Hook": "_hook",
    "JSONResponse": "_response",
    "NO_BODY_STATUS": "_transport",
    "Op": "_op",
    "PlainTextResponse": "_response",
    "RedirectResponse": "_response",
    "Response": "_response",
    "Route": "_route",
    "Router": "_router",
    "Schema": "_schema",
    "StreamingResponse": "_response",
    "Table": "_table",
    "finalize_transport_response": "_transport",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
