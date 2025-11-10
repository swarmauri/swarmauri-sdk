from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, MutableMapping, Sequence

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .template import render_shell

ManifestBuilder = Callable[[], Mapping[str, Any] | MutableMapping[str, Any] | Any]


@dataclass(slots=True)
class ScriptSpec:
    src: str | None = None
    content: str | None = None
    type: str = "module"
    async_attr: bool = False
    defer: bool = False


@dataclass(slots=True)
class RouterOptions:
    manifest_url: str = "./manifest.json"
    page_param: str = "page"
    default_page_id: str | None = None
    history: Literal["history", "hash"] = "history"
    hydrate_site_meta: bool = True

    @property
    def enable_multipage(self) -> bool:
        return bool(self.default_page_id) or bool(self.page_param)


@dataclass(slots=True)
class LayoutOptions:
    title: str | None = None
    accent_palette: dict[str, str] | None = None
    import_map_overrides: dict[str, str] | None = None
    extra_styles: Sequence[str] | None = None
    extra_scripts: Sequence[ScriptSpec] | None = None
    router: RouterOptions | None = None


@dataclass(slots=True)
class UIHooks:
    header_slot: str | None = None
    nav_slot: str | None = None
    content_slot: str | None = None
    footer_slot: str | None = None
    client_setup: str | None = None


DEFAULT_TITLE = "Layout Engine Dashboard"

DEFAULT_PALETTE = {
    "accent": "rgba(56, 189, 248, 0.75)",
    "panel": "rgba(15, 23, 42, 0.92)",
    "surface": "rgba(2, 6, 23, 1)",
    "text": "#e2e8f0",
}

_ASSETS_ROOT = Path(__file__).resolve().parent / "assets"
_LAYOUT_ENGINE_DIST = _ASSETS_ROOT / "layout-engine-vue"
_SWARMA_VUE_DIST = _ASSETS_ROOT / "swarma-vue"


def mount_layout_app(
    app: FastAPI,
    manifest_builder: ManifestBuilder,
    *,
    base_path: str = "/dashboard",
    title: str = DEFAULT_TITLE,
    layout_options: LayoutOptions | None = None,
    ui_hooks: UIHooks | None = None,
) -> None:
    """Mount the layout engine Vue runtime on an existing FastAPI app."""

    layout_options = layout_options or LayoutOptions()
    ui_hooks = ui_hooks or UIHooks()

    resolved_title = layout_options.title or title
    router_options = layout_options.router or RouterOptions()
    accent_palette = {**DEFAULT_PALETTE, **(layout_options.accent_palette or {})}

    import_map = {
        "vue": "https://cdn.jsdelivr.net/npm/vue@3/dist/vue.esm-browser.js",
        "eventemitter3": "https://cdn.jsdelivr.net/npm/eventemitter3@5/dist/eventemitter3.esm.js",
        "@swarmakit/vue": "./static/swarma-vue/vue.js",
    }
    if layout_options.import_map_overrides:
        import_map.update(layout_options.import_map_overrides)

    pre_boot_scripts = [
        _render_script(spec) for spec in layout_options.extra_scripts or []
    ]

    config_payload = {
        "title": resolved_title,
        "theme": {
            "accentPalette": accent_palette,
        },
        "router": {
            "manifestUrl": router_options.manifest_url,
            "pageParam": router_options.page_param,
            "defaultPageId": router_options.default_page_id,
            "history": router_options.history,
            "hydrateThemeFromManifest": router_options.hydrate_site_meta,
            "enableMultipage": router_options.enable_multipage,
        },
        "ui": {
            "headerSlot": ui_hooks.header_slot,
            "navSlot": ui_hooks.nav_slot,
            "contentSlot": ui_hooks.content_slot,
            "footerSlot": ui_hooks.footer_slot,
        },
        "clientSetup": ui_hooks.client_setup,
    }

    shell_html = render_shell(
        title=resolved_title,
        import_map=import_map,
        config_payload=config_payload,
        palette=accent_palette,
        bootstrap_module="./static/layout-engine-vue/mpa-bootstrap.js",
        extra_styles=layout_options.extra_styles,
        pre_boot_scripts=pre_boot_scripts,
    )

    norm_base = _normalize_base_path(base_path)
    router = _create_layout_router(manifest_builder, shell_html, router_options)
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


def _create_layout_router(
    manifest_builder: ManifestBuilder,
    shell_html: str,
    router_options: RouterOptions,
) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def layout_index(_: Request) -> HTMLResponse:  # noqa: D401
        return HTMLResponse(shell_html)

    @router.get("/manifest.json", response_class=JSONResponse)
    async def manifest_endpoint(request: Request) -> JSONResponse:
        manifest = await _call_builder(manifest_builder, request)
        payload = _normalize_manifest(manifest)
        if router_options.enable_multipage and router_options.page_param:
            requested = request.query_params.get(router_options.page_param)
            if requested:
                payload.setdefault("meta", {}).setdefault("page", {})["requested"] = (
                    requested
                )
        return JSONResponse(content=payload)

    return router


def _normalize_base_path(base_path: str) -> str:
    if not base_path:
        return "/"
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    if base_path != "/" and base_path.endswith("/"):
        base_path = base_path[:-1]
    return base_path or "/"


async def _call_builder(
    builder: ManifestBuilder, request: Request | None = None
) -> Any:
    if request is None:
        raise RuntimeError("manifest builder requires request context")
    result = builder(request)
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


def _render_script(spec: ScriptSpec) -> str:
    attrs: list[str] = []
    script_type = spec.type or "module"
    attrs.append(f'type="{script_type}"')
    if spec.async_attr:
        attrs.append("async")
    if spec.defer:
        attrs.append("defer")
    if spec.src:
        attrs.append(f'src="{spec.src}"')
    attrs_str = " ".join(attrs)
    if spec.content:
        return f"<script {attrs_str}>{spec.content}</script>"
    return f"<script {attrs_str}></script>"
