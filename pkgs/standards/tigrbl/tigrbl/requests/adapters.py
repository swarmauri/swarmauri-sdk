"""ASGI/WSGI adapters for constructing :class:`tigrbl.requests.Request`."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

from ._request import Request


def request_from_wsgi(router: Any, environ: dict[str, Any]) -> Request:
    method = (environ.get("REQUEST_METHOD") or "GET").upper()
    path = environ.get("PATH_INFO") or "/"
    script_name = environ.get("SCRIPT_NAME") or ""

    headers: dict[str, str] = {}
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            header_key = key[5:].replace("_", "-").lower()
            headers[header_key] = str(value)
    if "CONTENT_TYPE" in environ:
        headers["content-type"] = str(environ["CONTENT_TYPE"])

    query = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=True)

    try:
        length = int(environ.get("CONTENT_LENGTH") or "0")
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    return Request(
        method=method,
        path=path,
        headers=headers,
        query=query,
        path_params={},
        body=body,
        script_name=script_name,
        app=router,
    )


def request_from_asgi(router: Any, scope: dict[str, Any], body: bytes) -> Request:
    method = (scope.get("method") or "GET").upper()
    path = scope.get("path") or "/"
    headers: dict[str, str] = {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in scope.get("headers", [])
    }
    query = parse_qs(
        scope.get("query_string", b"").decode("latin-1"),
        keep_blank_values=True,
    )
    return Request(
        method=method,
        path=path,
        headers=headers,
        query=query,
        path_params={},
        body=body,
        script_name=scope.get("root_path") or "",
        app=router,
        scope=scope,
    )


__all__ = ["request_from_asgi", "request_from_wsgi"]
