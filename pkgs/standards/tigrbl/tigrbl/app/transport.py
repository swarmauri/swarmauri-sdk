"""ASGI/WSGI application adapters for router instances."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable

from tigrbl.middlewares import apply_middlewares
from tigrbl.transport.request import request_from_asgi, request_from_wsgi
from tigrbl.transport.response import Response, finalize_transport_response


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
        resp = await router._dispatch(req)
        headers, finalized_body = finalize_transport_response(
            scope,
            resp.status_code,
            [
                (k.encode("latin-1"), v.encode("latin-1"))
                for k, v in resp.headers.items()
            ],
            resp.body,
        )
        await send(
            {
                "type": "http.response.start",
                "status": resp.status_code,
                "headers": headers,
            }
        )
        await send(
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
            [
                (k.encode("latin-1"), v.encode("latin-1"))
                for k, v in resp.headers.items()
            ],
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

    start_response(resp.status_line(), resp.headers.as_list())
    return [resp.body]


__all__ = ["asgi_app", "wsgi_app"]
