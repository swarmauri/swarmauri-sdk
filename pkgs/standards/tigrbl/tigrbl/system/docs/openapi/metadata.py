"""OpenAPI/docs route metadata helpers."""

from __future__ import annotations

from typing import Any


def is_metadata_route(router: Any, route: Any) -> bool:
    if route.name in {"__openapi__", "__docs__"}:
        return True

    openapi_path = (
        router.openapi_url
        if router.openapi_url.startswith("/")
        else f"/{router.openapi_url}"
    )
    docs_path = (
        router.docs_url if router.docs_url.startswith("/") else f"/{router.docs_url}"
    )
    metadata_paths = {router.prefix + openapi_path, router.prefix + docs_path}

    route_path = route.path_template
    if route_path in metadata_paths:
        return True

    # When routers are mounted under an app prefix, routes may be re-registered
    # with the mount prefix while router.prefix remains unchanged.
    normalized_metadata_paths = {
        path if path == "/" else path.rstrip("/") for path in metadata_paths
    }
    normalized_route_path = route_path if route_path == "/" else route_path.rstrip("/")
    return normalized_route_path in normalized_metadata_paths
