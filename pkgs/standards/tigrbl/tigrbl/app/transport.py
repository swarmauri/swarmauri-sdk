"""ASGI/WSGI application adapters for router instances."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable

from tigrbl.middlewares import apply_middlewares
from tigrbl.requests.adapters import request_from_asgi, request_from_wsgi
from tigrbl.responses import Response
from tigrbl.responses._transport import finalize_transport_response


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
        body = b""
        more_body = True
        while more_body:
            message = await _receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        req = request_from_asgi(router, _scope, body)
        resp = await router._dispatch(req)
        headers, finalized_body = finalize_transport_response(
            _scope,
            resp.status_code,
            [(k.encode("latin-1"), v.encode("latin-1")) for k, v in resp.headers],
            resp.body,
        )
        await _send(
            {
                "type": "http.response.start",
                "status": resp.status_code,
                "headers": headers,
            }
        )
        await _send(
            {
                "type": "http.response.body",
                "body": finalized_body,
                "more_body": False,
            }
        )

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
        resp = asyncio.run(router._dispatch(req))
        headers, finalized_body = finalize_transport_response(
            {"method": req.method},
            resp.status_code,
            [(k.encode("latin-1"), v.encode("latin-1")) for k, v in resp.headers],
            resp.body,
        )
        _start_response(
            resp.status_line(),
            [(k.decode("latin-1"), v.decode("latin-1")) for k, v in headers],
        )
        return [finalized_body]

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


__all__ = ["asgi_app", "router_call", "wsgi_app"]
