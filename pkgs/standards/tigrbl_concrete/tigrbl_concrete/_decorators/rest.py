"""Reusable HTTP verb route decorators for router-like objects."""

from __future__ import annotations

from typing import Any, Callable

Handler = Callable[..., Any]


def get(router: Any, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
    return router.route(path, methods=["GET"], **kwargs)


def post(router: Any, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
    return router.route(path, methods=["POST"], **kwargs)


def put(router: Any, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
    return router.route(path, methods=["PUT"], **kwargs)


def patch(router: Any, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
    return router.route(path, methods=["PATCH"], **kwargs)


def delete(router: Any, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
    return router.route(path, methods=["DELETE"], **kwargs)


__all__ = ["get", "post", "put", "patch", "delete"]
