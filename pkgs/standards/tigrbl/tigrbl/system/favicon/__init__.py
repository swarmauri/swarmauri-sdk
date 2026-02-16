from __future__ import annotations

from pathlib import Path
from typing import Any

from ...responses import FileResponse, RedirectResponse

FAVICON_PATH = Path(__file__).with_name("assets") / "favicon.svg"


def favicon_endpoint(*, favicon_path: str | Path | None = FAVICON_PATH):
    """Build an endpoint function that serves the configured favicon."""

    resolved = Path(FAVICON_PATH if favicon_path is None else favicon_path)

    def _favicon() -> FileResponse:
        if resolved.suffix.lower() == ".ico":
            return FileResponse(str(resolved), media_type="image/x-icon")
        return FileResponse(str(resolved), media_type="image/svg+xml")

    return _favicon


def favicon_ico_redirect_endpoint(path: str = "/favicon.svg"):
    """Build an endpoint function that redirects ``/favicon.ico`` to SVG."""

    def _favicon_redirect() -> RedirectResponse:
        return RedirectResponse(url=path, status_code=307)

    return _favicon_redirect


def _remove_existing_favicon_routes(router: Any, *paths: str) -> None:
    """Remove existing routes matching favicon paths so remounts take precedence."""

    path_set = set(paths)
    routes = getattr(router, "_routes", None)
    if routes is None:
        routes = getattr(router, "routes", None)
    if routes is None:
        return

    filtered = [
        route
        for route in routes
        if (getattr(route, "path_template", None) or getattr(route, "path", None))
        not in path_set
    ]

    if hasattr(router, "_routes"):
        router._routes = filtered
    if hasattr(router, "routes"):
        router.routes = filtered


def mount_favicon(
    router: Any,
    *,
    path: str = "/favicon.svg",
    ico_path: str = "/favicon.ico",
    favicon_path: str | Path | None = FAVICON_PATH,
    name: str = "__favicon__",
) -> Any:
    """Mount a favicon endpoint onto ``router``."""

    resolved = Path(FAVICON_PATH if favicon_path is None else favicon_path)

    _remove_existing_favicon_routes(router, path, ico_path)

    if resolved.suffix.lower() == ".svg":
        router.add_api_route(
            path,
            favicon_endpoint(favicon_path=resolved),
            methods=["GET"],
            name=name,
            include_in_schema=False,
        )
        router.add_api_route(
            ico_path,
            favicon_ico_redirect_endpoint(path=path),
            methods=["GET"],
            name=f"{name}_ico_redirect",
            include_in_schema=False,
        )
        return router

    router.add_api_route(
        ico_path,
        favicon_endpoint(favicon_path=resolved),
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = [
    "FAVICON_PATH",
    "favicon_endpoint",
    "favicon_ico_redirect_endpoint",
    "mount_favicon",
]
