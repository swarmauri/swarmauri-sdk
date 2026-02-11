"""Core routing runtime dispatch and handler execution helpers."""

from __future__ import annotations

import inspect
from typing import Any, Callable

from ..api.resolve import (
    invoke_dependency,
    resolve_handler_kwargs,
    resolve_route_dependencies,
)
from ..deps.starlette import Response as StarletteResponse
from ..response.stdapi import Response
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..transport.request import Request


async def dispatch(router: Any, req: Request) -> Response:
    candidates = [r for r in router._routes if req.method in r.methods]
    candidates.sort(key=router._route_match_priority)
    for route in candidates:
        match = route.pattern.match(req.path)
        if not match:
            continue
        req2 = Request(
            method=req.method,
            path=req.path,
            headers=req.headers,
            query=req.query,
            path_params={k: v for k, v in match.groupdict().items()},
            body=req.body,
            script_name=req.script_name,
            app=router,
            state=req.state,
            scope=req.scope,
        )
        return await call_handler(router, route, req2)

    for route in router._routes:
        if route.pattern.match(req.path):
            allowed = ",".join(sorted(route.methods))
            return Response.json(
                {"detail": "Method Not Allowed"},
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                headers={"allow": allowed},
            )

    return Response.json({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)


async def call_handler(router: Any, route: Any, req: Request) -> Response:
    dependency_cleanups: list[Callable[[], Any]] = []
    setattr(req.state, "_dependency_cleanups", dependency_cleanups)
    try:
        await resolve_route_dependencies(router, route, req)
        kwargs = await resolve_handler_kwargs(router, route, req)
        out = route.handler(**kwargs)
        if inspect.isawaitable(out):
            out = await out
    except HTTPException as he:
        return Response.json(
            {"detail": he.detail},
            status_code=he.status_code,
            headers=he.headers,
        )
    finally:
        for cleanup in reversed(dependency_cleanups):
            try:
                result = cleanup()
                if inspect.isawaitable(result):
                    await result
            except Exception:
                pass

    if isinstance(out, Response):
        return out
    if isinstance(out, StarletteResponse):
        body = bytes(getattr(out, "body", b"") or b"")
        if not body and hasattr(out, "body_iterator"):
            chunks: list[bytes] = []
            body_iter = getattr(out, "body_iterator")
            if body_iter is not None:
                if hasattr(body_iter, "__aiter__"):
                    async for chunk in body_iter:
                        chunks.append(
                            chunk.encode("utf-8")
                            if isinstance(chunk, str)
                            else bytes(chunk)
                        )
                else:
                    for chunk in body_iter:
                        chunks.append(
                            chunk.encode("utf-8")
                            if isinstance(chunk, str)
                            else bytes(chunk)
                        )
                body = b"".join(chunks)
        if not body and hasattr(out, "path"):
            path = getattr(out, "path")
            if isinstance(path, str):
                with open(path, "rb") as fp:
                    body = fp.read()
        headers = list(getattr(out, "headers", {}).items())
        media_type = getattr(out, "media_type", None)
        if media_type and not any(k.lower() == "content-type" for k, _ in headers):
            headers.append(("content-type", media_type))
        return Response(
            status_code=getattr(out, "status_code", 200),
            headers=headers,
            body=body,
        )

    code = route.status_code if route.status_code is not None else 200
    if out is None:
        if code == 204:
            return Response(
                status_code=204, headers=[("content-length", "0")], body=b""
            )
        return Response.json(None, status_code=code)
    if isinstance(out, (str, bytes, bytearray)):
        return Response(
            status_code=code,
            headers=[("content-type", "application/octet-stream")],
            body=bytes(out),
        )
    return Response.json(out, status_code=code)


def is_metadata_route(router: Any, route: Any) -> bool:
    from ..system.docs.openapi.metadata import is_metadata_route as _is_metadata_route

    return _is_metadata_route(router, route)


_resolve_route_dependencies = resolve_route_dependencies
_resolve_handler_kwargs = resolve_handler_kwargs
_invoke_dependency = invoke_dependency
