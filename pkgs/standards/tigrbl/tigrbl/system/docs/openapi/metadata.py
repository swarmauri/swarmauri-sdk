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
    return route.path_template in metadata_paths
