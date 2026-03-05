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
    "ForeignKey": "_storage",
    "Table": "_table",
    "Template": "_response",
    "TableRegistry": "_table_registry",
    "Response": "_response",
    "TransportResponse": "_response",
    "JSONResponse": "_json_response",
    "HTMLResponse": "_html_response",
    "PlainTextResponse": "_plain_text_response",
    "StreamingResponse": "_streaming_response",
    "DefaultSession": "_session",
    "FileResponse": "_file_response",
    "RedirectResponse": "_redirect_response",
    "Request": "_request",
    "Body": "_body",
    "Depends": "dependencies",
    "APIKey": "_security",
    "HTTPBearer": "_security",
    "OAuth2": "_security",
    "OpenIdConnect": "_security",
    "MutualTLS": "_security",
    "TigrblApp": "tigrbl_app",
    "TigrblRouter": "tigrbl_router",
    "BackgroundTask": "_response",
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
