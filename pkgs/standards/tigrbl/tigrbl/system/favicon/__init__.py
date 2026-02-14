from __future__ import annotations

from pathlib import Path
from typing import Any

from ...response.stdapi import FileResponse

FAVICON_PATH = Path(__file__).with_name("assets") / "favicon.svg"


def favicon_endpoint(*, favicon_path: str | Path | None = FAVICON_PATH):
    """Build an endpoint function that serves the configured favicon."""

    resolved = Path(FAVICON_PATH if favicon_path is None else favicon_path)

    def _favicon() -> FileResponse:
        return FileResponse(str(resolved), media_type="image/svg+xml")

    return _favicon


def mount_favicon(
    router: Any,
    *,
    path: str = "/favicon.ico",
    favicon_path: str | Path | None = FAVICON_PATH,
    name: str = "__favicon__",
) -> Any:
    """Mount a favicon endpoint onto ``router``."""

    router.add_api_route(
        path,
        favicon_endpoint(favicon_path=favicon_path),
        methods=["GET"],
        name=name,
        include_in_schema=False,
    )
    return router


__all__ = ["FAVICON_PATH", "favicon_endpoint", "mount_favicon"]
