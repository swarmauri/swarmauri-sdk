from __future__ import annotations

from pathlib import Path
from typing import Any

from ..._concrete import FileResponse, RedirectResponse

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

    def _prune_routes(target: Any) -> bool:
        routes = getattr(target, "_routes", None)
        if routes is None:
            routes = getattr(target, "routes", None)
        if routes is None:
            return False

        filtered = [
            route
            for route in routes
            if (getattr(route, "path_template", None) or getattr(route, "path", None))
            not in path_set
        ]

        if hasattr(target, "_routes"):
            target._routes = filtered
        if hasattr(target, "routes"):
            target.routes = filtered
        return True

    _prune_routes(router)

    nested_router = getattr(router, "router", None)
    if nested_router is not None:
        _prune_routes(nested_router)


def mount_favicon(
    router: Any,
    *,
    file_path: str | Path | None = FAVICON_PATH,
    svg_path: str = "/favicon.svg",
    ico_path: str = "/favicon.ico",
    prefix: str = "",
    name: str = "__favicon__",
) -> Any:
    """Mount a favicon endpoint onto ``router``."""

    resolved = Path(FAVICON_PATH if file_path is None else file_path)

    base_prefix = f"/{prefix.strip('/')}" if prefix else ""
    mounted_svg_path = f"{base_prefix}{svg_path}"
    mounted_ico_path = f"{base_prefix}{ico_path}"

    # ``TigrblApp`` installs a default root-level favicon during initialization.
    # When callers remount under a custom prefix, remove those defaults so only
    # the explicit mount location remains active.
    default_svg_path = f"{svg_path}" if svg_path.startswith("/") else f"/{svg_path}"
    default_ico_path = f"{ico_path}" if ico_path.startswith("/") else f"/{ico_path}"

    _remove_existing_favicon_routes(
        router,
        mounted_svg_path,
        mounted_ico_path,
        default_svg_path,
        default_ico_path,
    )

    def _register(path: str, endpoint: Any, route_name: str) -> None:
        add_route = getattr(router, "add_route", None)
        if callable(add_route):
            add_route(
                path,
                endpoint,
                methods=["GET"],
                name=route_name,
                include_in_schema=False,
            )
            return

        route = getattr(router, "route", None)
        if not callable(route):
            raise AttributeError(
                "Router-like object must provide add_route(...) or route(...)."
            )
        route(
            path,
            methods=["GET"],
            name=route_name,
            include_in_schema=False,
        )(endpoint)

    if resolved.suffix.lower() == ".svg":
        _register(mounted_svg_path, favicon_endpoint(favicon_path=resolved), name)
        _register(
            mounted_ico_path,
            favicon_ico_redirect_endpoint(path=f"{base_prefix}{svg_path}"),
            f"{name}_ico_redirect",
        )
        return router

    _register(mounted_ico_path, favicon_endpoint(favicon_path=resolved), name)
    return router


__all__ = [
    "FAVICON_PATH",
    "favicon_endpoint",
    "favicon_ico_redirect_endpoint",
    "mount_favicon",
]
