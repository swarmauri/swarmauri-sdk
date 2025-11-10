from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, MutableMapping, Sequence

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..vue.realtime import RealtimeBinding, RealtimeOptions, WebsocketMuxHub
from .template import render_shell

ManifestBuilder = Callable[[], Mapping[str, Any] | MutableMapping[str, Any] | Any]


@dataclass(slots=True)
class SvelteScriptSpec:
    src: str | None = None
    content: str | None = None
    type: str = "module"
    async_attr: bool = False
    defer: bool = False


@dataclass(slots=True)
class SvelteRouterOptions:
    manifest_url: str = "./manifest.json"
    page_param: str = "page"
    default_page_id: str | None = None
    history: Literal["history", "hash"] = "history"
    hydrate_site_meta: bool = True

    @property
    def enable_multipage(self) -> bool:
        return bool(self.default_page_id) or bool(self.page_param)


@dataclass(slots=True)
class SvelteLayoutOptions:
    title: str | None = None
    accent_palette: dict[str, str] | None = None
    import_map_overrides: dict[str, str] | None = None
    extra_styles: Sequence[str] | None = None
    extra_scripts: Sequence[SvelteScriptSpec] | None = None
    router: SvelteRouterOptions | None = None


@dataclass(slots=True)
class SvelteUIHooks:
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
_LAYOUT_ENGINE_DIST = _ASSETS_ROOT / "layout-engine-svelte"


def mount_svelte_app(
    app: FastAPI,
    manifest_builder: ManifestBuilder,
    *,
    base_path: str = "/dashboard",
    title: str = DEFAULT_TITLE,
    layout_options: SvelteLayoutOptions | None = None,
    ui_hooks: SvelteUIHooks | None = None,
    realtime: RealtimeOptions | None = None,
) -> None:
    layout_options = layout_options or SvelteLayoutOptions()
    ui_hooks = ui_hooks or SvelteUIHooks()

    resolved_title = layout_options.title or title
    router_options = layout_options.router or SvelteRouterOptions()
    accent_palette = {**DEFAULT_PALETTE, **(layout_options.accent_palette or {})}

    import_map = {
        "svelte": "https://cdn.jsdelivr.net/npm/svelte@4.2.0",
        "@swarmakit/layout-engine-svelte": "./static/layout-engine-svelte/index.js",
        "@swarmakit/svelte": "./static/swarma-svelte/svelte.js",
    }
    if layout_options.import_map_overrides:
        import_map.update(layout_options.import_map_overrides)

    pre_boot_scripts = [
        _render_script(spec) for spec in layout_options.extra_scripts or []
    ]

    norm_base = _normalize_base_path(base_path)
    realtime_payload = {"enabled": False}
    ws_route: str | None = None
    hub: WebsocketMuxHub | None = None
    if realtime:
        ws_route = _join_paths(norm_base, realtime.path)
        hub = WebsocketMuxHub(path=realtime.path)
        realtime_payload = {
            "enabled": True,
            "path": ws_route,
            "channels": [channel.id for channel in realtime.channels],
            "autoSubscribe": realtime.auto_subscribe,
        }
        binding_script = _render_binding_script(realtime.bindings)
        if binding_script:
            if ui_hooks.client_setup:
                ui_hooks.client_setup = f"{ui_hooks.client_setup}\n{binding_script}"
            else:
                ui_hooks.client_setup = binding_script

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
        "realtime": realtime_payload,
    }

    shell_html = render_shell(
        title=resolved_title,
        import_map=import_map,
        config_payload=config_payload,
        palette=accent_palette,
        bootstrap_module="./static/layout-engine-svelte/mpa-bootstrap.js",
        extra_styles=layout_options.extra_styles,
        pre_boot_scripts=pre_boot_scripts,
    )

    router = _create_layout_router(
        manifest_builder,
        shell_html,
        router_options,
        realtime=realtime,
        ws_route=ws_route,
    )
    app.include_router(router, prefix=norm_base if norm_base != "/" else "")

    static_prefix = "" if norm_base == "/" else norm_base
    app.mount(
        f"{static_prefix}/static/layout-engine-svelte",
        StaticFiles(directory=_LAYOUT_ENGINE_DIST, html=False),
        name="layout-engine-svelte",
    )
    app.mount(
        f"{static_prefix}/static/swarma-svelte",
        StaticFiles(
            directory=_ASSETS_ROOT / "swarma-svelte",
            html=False,
        ),
        name="swarma-svelte",
    )
    if realtime and hub and ws_route:
        hub.mount(app, ws_route)

        async def _start_realtime() -> None:
            await hub.start_publishers(realtime.publishers)

        async def _stop_realtime() -> None:
            await hub.stop_publishers()
            await hub.disconnect_all()

        app.add_event_handler("startup", _start_realtime)
        app.add_event_handler("shutdown", _stop_realtime)
        app.state.layout_engine_svelte_realtime = hub


def _create_layout_router(
    manifest_builder: ManifestBuilder,
    shell_html: str,
    router_options: SvelteRouterOptions,
    *,
    realtime: RealtimeOptions | None,
    ws_route: str | None,
) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def layout_index(_: Request) -> HTMLResponse:
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
        _inject_realtime_metadata(payload, realtime, ws_route)
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


def _join_paths(base_path: str, suffix: str) -> str:
    if not suffix:
        return base_path or "/"
    if not suffix.startswith("/"):
        suffix = "/" + suffix
    if base_path in ("", "/"):
        return suffix
    if suffix == "/":
        return base_path
    return f"{base_path}{suffix}"


async def _call_builder(
    builder: ManifestBuilder, request: Request | None = None
) -> Any:
    if request is None:
        raise RuntimeError("manifest builder requires request context")
    result = builder(request)
    if inspect.isawaitable(result):
        return await result
    return result


def _normalize_manifest(manifest: Any) -> MutableMapping[str, Any]:
    if manifest is None:
        raise ValueError("Manifest builder returned None")
    if hasattr(manifest, "model_dump"):
        return manifest.model_dump()
    if hasattr(manifest, "model_dump_json"):
        return manifest.model_dump()
    if isinstance(manifest, Mapping):
        return dict(manifest)
    raise TypeError(
        "Manifest builder must return a Mapping or pydantic model; got "
        f"{type(manifest)!r}"
    )


def _inject_realtime_metadata(
    payload: MutableMapping[str, Any],
    realtime: RealtimeOptions | None,
    ws_route: str | None,
) -> None:
    if not realtime or not ws_route:
        return
    rt_channels = payload.setdefault("channels", [])
    existing_ids = {
        entry.get("id")
        for entry in rt_channels
        if isinstance(entry, Mapping) and isinstance(entry.get("id"), str)
    }
    for channel in realtime.channels:
        if channel.id in existing_ids:
            continue
        rt_channels.append(channel.as_manifest())

    ws_routes = payload.setdefault("ws_routes", [])
    existing_paths = {
        entry.get("path")
        for entry in ws_routes
        if isinstance(entry, Mapping) and isinstance(entry.get("path"), str)
    }
    if ws_route not in existing_paths:
        ws_routes.append(
            {
                "path": ws_route,
                "channels": [channel.id for channel in realtime.channels],
            }
        )


def _render_binding_script(bindings: Sequence[RealtimeBinding]) -> str:
    if not bindings:
        return ""
    payload = json.dumps(
        [binding.as_payload() for binding in bindings],
        separators=(",", ":"),
    )
    return (
        "(function realtimeBindingBootstrap() {\n"
        "  if (!context || !context.manifest) {\n"
        "    console.warn('[layout-engine] realtime bindings require manifest context.');\n"
        "    return;\n"
        "  }\n"
        "  const manifest = context.manifest;\n"
        f"  const bindings = {payload};\n"
        "  const EVENT_NAME = 'layout-engine:channel';\n"
        "  const getValue = (payload, path) => {\n"
        "    if (!path) return payload;\n"
        "    return path.split('.').reduce((acc, key) => {\n"
        "      if (acc === undefined || acc === null) return undefined;\n"
        "      const next = acc[key];\n"
        "      return next === undefined ? undefined : next;\n"
        "    }, payload);\n"
        "  };\n"
        "  const applyBinding = (binding, payload) => {\n"
        "    const tiles = Array.isArray(manifest.tiles) ? manifest.tiles : [];\n"
        "    const target = tiles.find((tile) => tile.id === binding.tileId);\n"
        "    if (!target) return;\n"
        "    target.props = target.props && typeof target.props === 'object' ? target.props : {};\n"
        "    for (const [prop, path] of Object.entries(binding.fields || {})) {\n"
        "      const value = getValue(payload, path);\n"
        "      if (value !== undefined) {\n"
        "        target.props[prop] = value;\n"
        "      }\n"
        "    }\n"
        "  };\n"
        "  const handler = (event) => {\n"
        "    const detail = event.detail || {};\n"
        "    for (const binding of bindings) {\n"
        "      if (binding.channel !== detail.channel) continue;\n"
        "      applyBinding(binding, detail.payload || {});\n"
        "    }\n"
        "  };\n"
        "  window.addEventListener(EVENT_NAME, handler);\n"
        "})();\n"
    )


def _render_script(spec: SvelteScriptSpec) -> str:
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
