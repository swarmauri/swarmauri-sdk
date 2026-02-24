"""ASGI3/WSGI gateway contract and reference transport implementations.

Gateway contract
----------------
* `asgi_app(router, scope, receive, send)` is an ASGI3 callable surface that:
  - handles lifespan messages when `scope['type'] == 'lifespan'`
  - dispatches HTTP requests through `router._dispatch(Request)`
  - wraps the core endpoint with router middleware in declaration order
  - allows middleware short-circuiting by not calling downstream
* `wsgi_app(router, environ, start_response)` is the WSGI entrypoint with the
  same dispatch + middleware semantics.

Middleware wrapping rules
-------------------------
* Router middleware is read from `router._middlewares` as
  `[(middleware_cls, options), ...]`.
* The first declared middleware is the outermost wrapper.
* Middleware classes are instantiated as `middleware_cls(app, **options)`.
* Short-circuit behavior is middleware-defined: if a middleware does not invoke
  its downstream `app`, execution stops at that layer.
"""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable, Protocol, TypeAlias

from tigrbl.transport.request import request_from_asgi, request_from_wsgi
from tigrbl.transport.response import Response, finalize_transport_response


ASGIScope: TypeAlias = dict[str, Any]
ASGIReceive: TypeAlias = Callable[[], Any]
ASGISend: TypeAlias = Callable[[dict[str, Any]], Any]
WSGIEnviron: TypeAlias = dict[str, Any]
WSGIStartResponse: TypeAlias = Callable[..., Any]


class ASGI3Gateway(Protocol):
    async def __call__(
        self,
        router: Any,
        scope: ASGIScope,
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None: ...


class WSGIGateway(Protocol):
    def __call__(
        self,
        router: Any,
        environ: WSGIEnviron,
        start_response: WSGIStartResponse,
    ) -> list[bytes]: ...


def wrap_middleware_stack(app: Any, router: Any) -> Any:
    """Wrap ``app`` using ``router._middlewares`` in declaration order."""
    middleware_stack = list(getattr(router, "_middlewares", []))
    wrapped = app
    for middleware_class, options in reversed(middleware_stack):
        wrapped = middleware_class(wrapped, **(options or {}))
    return wrapped


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

    app = wrap_middleware_stack(_endpoint, router)
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

    app = wrap_middleware_stack(_endpoint, router)

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


__all__ = [
    "ASGI3Gateway",
    "WSGIGateway",
    "ASGIScope",
    "ASGIReceive",
    "ASGISend",
    "WSGIEnviron",
    "WSGIStartResponse",
    "wrap_middleware_stack",
    "asgi_app",
    "wsgi_app",
]
