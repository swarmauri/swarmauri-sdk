from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .template import render_shell

ManifestBuilder = Callable[[], Mapping[str, Any] | MutableMapping[str, Any] | Any]

_ASSETS_ROOT = Path(__file__).resolve().parent / "assets"
_LAYOUT_ENGINE_DIST = _ASSETS_ROOT / "layout-engine-vue"
_SWARMA_VUE_DIST = _ASSETS_ROOT / "swarma-vue"


def create_layout_router(
    manifest_builder: ManifestBuilder,
    *,
    title: str = "Layout Engine Dashboard",
) -> APIRouter:
    """Create an APIRouter that serves the layout shell and manifest."""

    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def layout_index(_: Request) -> HTMLResponse:  # noqa: D401
        html = render_shell(title=title)
        return HTMLResponse(html)

    @router.get("/manifest.json", response_class=JSONResponse)
    async def manifest_endpoint(_: Request) -> JSONResponse:
        manifest = await _call_builder(manifest_builder)
        payload = _normalize_manifest(manifest)
        return JSONResponse(content=payload)

    return router


def mount_layout_app(
    app: FastAPI,
    manifest_builder: ManifestBuilder,
    *,
    base_path: str = "/dashboard",
    title: str = "Layout Engine Dashboard",
) -> None:
    """Mount the layout engine Vue runtime on an existing FastAPI app."""

    norm_base = _normalize_base_path(base_path)
    router = create_layout_router(manifest_builder, title=title)
    app.include_router(router, prefix=norm_base if norm_base != "/" else "")

    static_prefix = "" if norm_base == "/" else norm_base
    app.mount(
        f"{static_prefix}/static/layout-engine-vue",
        StaticFiles(directory=_LAYOUT_ENGINE_DIST, html=False),
        name="layout-engine-vue",
    )
    app.mount(
        f"{static_prefix}/static/swarma-vue",
        StaticFiles(directory=_SWARMA_VUE_DIST, html=False),
        name="swarma-vue",
    )


def _normalize_base_path(base_path: str) -> str:
    if not base_path:
        return "/"
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    if base_path != "/" and base_path.endswith("/"):
        base_path = base_path[:-1]
    return base_path or "/"


async def _call_builder(builder: ManifestBuilder) -> Any:
    result = builder()
    if inspect.isawaitable(result):
        return await result
    return result


def _normalize_manifest(manifest: Any) -> Mapping[str, Any]:
    if manifest is None:
        raise ValueError("Manifest builder returned None")
    if hasattr(manifest, "model_dump"):
        return manifest.model_dump()
    if hasattr(manifest, "model_dump_json"):
        return manifest.model_dump()
    if isinstance(manifest, Mapping):
        return manifest  # type: ignore[return-value]
    raise TypeError(
        "Manifest builder must return a Mapping or pydantic model; got "
        f"{type(manifest)!r}"
    )
