"""Concrete generic class implementations for tigrbl."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "App": "_app",
    "Column": "_column",
    "Engine": "_engine",
    "Hook": "_hook",
    "Op": "_op",
    "Route": "_route",
    "Router": "_router",
    "Schema": "_schema",
    "Table": "_table",
    "Template": "_response",
    "Response": "_response",
    "TransportResponse": "_transport_response",
    "JSONResponse": "_transport_response",
    "HTMLResponse": "_transport_response",
    "PlainTextResponse": "_transport_response",
    "StreamingResponse": "_transport_response",
    "FileResponse": "_transport_response",
    "RedirectResponse": "_transport_response",
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
