"""ASGI/WSGI transport adapters for router instances."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable

from tigrbl.middlewares import apply_middlewares
from tigrbl.requests.adapters import request_from_asgi, request_from_wsgi
from tigrbl.responses import Response
from tigrbl.responses._transport import finalize_transport_response


async def _run_lifecycle_hook(router: Any, phase: str) -> None:
    run_method = getattr(router, f"run_{phase}", None)
    if callable(run_method):
        await run_method()
        return

    lifecycle = getattr(router, "lifecycle", None)
    if lifecycle is not None:
        lifecycle_method = getattr(lifecycle, f"run_{phase}", None)
        if callable(lifecycle_method):
            await lifecycle_method()


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
                    await _run_lifecycle_hook(router, "startup")
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
                    await _run_lifecycle_hook(router, "shutdown")
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
        endpoint_scope: dict[str, Any],
        endpoint_receive: Callable,
        endpoint_send: Callable,
    ) -> None:
        body = b""
        more_body = True
        while more_body:
            message = await endpoint_receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        req = request_from_asgi(router, endpoint_scope, body)
        resp = await router._dispatch(req)
        headers, finalized_body = finalize_transport_response(
            endpoint_scope,
            resp.status_code,
            [
                (k.encode("latin-1"), v.encode("latin-1"))
                for k, v in resp.headers.items()
            ],
            resp.body,
        )
        await endpoint_send(
            {
                "type": "http.response.start",
                "status": resp.status_code,
                "headers": headers,
            }
        )
        await endpoint_send(
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
        endpoint_environ: dict[str, Any],
        endpoint_start_response: Callable[..., Any],
    ) -> list[bytes]:
        req = request_from_wsgi(router, endpoint_environ)
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
        endpoint_start_response(
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


def http_app_call(router: Any, *args: Any, **kwargs: Any):
    """Dispatch ASGI/WSGI call shapes to transport implementations.

    Supported forms:
    - WSGI: ``(environ: dict, start_response: Callable)`` -> ``wsgi_app``.
    - ASGI 3: ``(scope: dict, receive: Callable, send: Callable)`` -> ``asgi_app``.
    - ASGI 2: ``(scope: dict)`` -> returns ``(receive, send)`` async callable.
    """

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


__all__ = ["asgi_app", "wsgi_app", "http_app_call"]
