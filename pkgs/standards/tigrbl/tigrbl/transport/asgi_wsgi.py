"""ASGI and WSGI runtime adapters for stdapi routers."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable
from urllib.parse import parse_qs

from tigrbl.middlewares import apply_middlewares
from tigrbl.requests._request import Request
from tigrbl.responses._response import Response


_BODYLESS_STATUS_CODES = {204, 304}


def _normalize_http_response(resp: Response, method: str) -> Response:
    """Normalize payload/body headers before writing to ASGI/WSGI transports."""

    method_upper = method.upper()
    is_bodyless_status = (
        100 <= resp.status_code < 200 or resp.status_code in _BODYLESS_STATUS_CODES
    )
    should_strip_body = is_bodyless_status or method_upper == "HEAD"

    headers = [(k, v) for k, v in resp.headers]

    if should_strip_body:
        resp.body = b""
        headers = [
            (k, v)
            for k, v in headers
            if k.lower() not in {"content-length", "transfer-encoding"}
        ]
    else:
        body_length = str(len(resp.body))
        has_content_length = False
        normalized_headers: list[tuple[str, str]] = []
        for key, value in headers:
            if key.lower() == "content-length":
                normalized_headers.append((key, body_length))
                has_content_length = True
            else:
                normalized_headers.append((key, value))
        if not has_content_length:
            normalized_headers.append(("content-length", body_length))
        headers = normalized_headers

    resp.headers = headers
    return resp


async def asgi_app(
    router: Any,
    scope: dict[str, Any],
    receive: Callable,
    send: Callable,
) -> None:
    scope_type = scope.get("type")

    if scope_type == "lifespan":
        while True:
            message = await receive()
            message_type = message.get("type")

            if message_type == "lifespan.startup":
                try:
                    run_handlers = getattr(router, "run_event_handlers", None)
                    if callable(run_handlers):
                        await run_handlers("startup")
                    await send({"type": "lifespan.startup.complete"})
                except Exception as exc:  # pragma: no cover - defensive
                    await send(
                        {
                            "type": "lifespan.startup.failed",
                            "message": str(exc),
                        }
                    )
                    return

            elif message_type == "lifespan.shutdown":
                try:
                    run_handlers = getattr(router, "run_event_handlers", None)
                    if callable(run_handlers):
                        await run_handlers("shutdown")
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as exc:  # pragma: no cover - defensive
                    await send(
                        {
                            "type": "lifespan.shutdown.failed",
                            "message": str(exc),
                        }
                    )
                return

            else:  # pragma: no cover - unexpected lifespan frame
                return

    if scope_type != "http":
        await send(
            {
                "type": "http.response.start",
                "status": 500,
                "headers": [],
            }
        )
        await send({"type": "http.response.body", "body": b""})
        return

    async def _endpoint(
        _scope: dict[str, Any], _receive: Callable, _send: Callable
    ) -> None:
        del _scope, _receive, _send

        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        req = request_from_asgi(router, scope, body)
        resp = _normalize_http_response(await router._dispatch(req), req.method)
        await send(
            {
                "type": "http.response.start",
                "status": resp.status_code,
                "headers": [
                    (k.encode("latin-1"), v.encode("latin-1")) for k, v in resp.headers
                ],
            }
        )
        await send({"type": "http.response.body", "body": resp.body})

    app = apply_middlewares(_endpoint, list(getattr(router, "_middlewares", [])))
    await app(scope, receive, send)


def wsgi_app(
    router: Any,
    environ: dict[str, Any],
    start_response: Callable[..., Any],
) -> list[bytes]:
    def _endpoint(
        _environ: dict[str, Any], _start_response: Callable[..., Any]
    ) -> list[bytes]:
        req = request_from_wsgi(router, _environ)
        resp = _normalize_http_response(asyncio.run(router._dispatch(req)), req.method)
        _start_response(resp.status_line(), resp.headers)
        return [resp.body]

    app = apply_middlewares(_endpoint, list(getattr(router, "_middlewares", [])))

    try:
        return app(environ, start_response)
    except Exception as exc:  # pragma: no cover - defensive
        if router.debug:
            tb = traceback.format_exc()
            resp = Response.json({"detail": str(exc), "traceback": tb}, status_code=500)
        else:
            resp = Response.json({"detail": "Internal Server Error"}, status_code=500)

    start_response(resp.status_line(), resp.headers)
    return [resp.body]


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


def router_call(router: Any, *args: Any, **kwargs: Any):
    del kwargs
    if len(args) == 2 and isinstance(args[0], dict) and callable(args[1]):
        return wsgi_app(router, args[0], args[1])
    if len(args) == 1 and isinstance(args[0], dict):
        scope = args[0]

        async def _asgi2_instance(receive: Callable, send: Callable) -> None:
            await asgi_app(router, scope, receive, send)

        return _asgi2_instance
    if len(args) == 3 and isinstance(args[0], dict):
        return asgi_app(router, args[0], args[1], args[2])
    raise TypeError("Invalid ASGI/WSGI invocation")
