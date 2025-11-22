from __future__ import annotations

import inspect
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, MutableMapping, Sequence

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .template import render_shell
from .events import UiEvent, UiEventResult
from .realtime import RealtimeBinding, RealtimeOptions, WebsocketMuxHub
from .validation import validate_client_setup_code, validate_event_payload
from .rate_limit import InMemoryRateLimiter

logger = logging.getLogger(__name__)

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
    enable_rate_limiting: bool = False
    rate_limit_requests: int = 60
    rate_limit_window: int = 60


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
    realtime: RealtimeOptions | None = None,
    events: Sequence[UiEvent] | Mapping[str, UiEvent] | None = None,
) -> None:
    """Mount the layout engine Vue runtime on an existing FastAPI app."""

    layout_options = layout_options or LayoutOptions()
    ui_hooks = ui_hooks or UIHooks()

    # Validate client_setup code for security issues
    if ui_hooks.client_setup:
        try:
            validate_client_setup_code(ui_hooks.client_setup)
        except ValueError as e:
            logger.error(f"Client setup validation failed: {e}")
            raise ValueError(
                f"Security validation failed for client_setup: {e}"
            ) from e

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

    norm_base = _normalize_base_path(base_path)
    event_registry = _normalize_events(events)
    events_payload = {
        "enabled": bool(event_registry),
        "baseUrl": _join_paths(norm_base, "/events"),
        "items": [entry.describe() for entry in event_registry.values()],
    }

    # Setup rate limiter if enabled
    rate_limiter: InMemoryRateLimiter | None = None
    if layout_options.enable_rate_limiting:
        rate_limiter = InMemoryRateLimiter(
            max_requests=layout_options.rate_limit_requests,
            window_seconds=layout_options.rate_limit_window,
        )
        rate_limiter.start_cleanup()
    realtime_payload = {"enabled": False}
    ws_route: str | None = None
    hub: WebsocketMuxHub | None = None
    if realtime:
        ws_route = _join_paths(norm_base, realtime.path)
        hub = WebsocketMuxHub(
            path=realtime.path,
            auth_handler=realtime.auth_handler,
            max_subscriptions_per_client=realtime.max_subscriptions_per_client,
        )
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
        "events": events_payload,
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

    router = _create_layout_router(
        manifest_builder,
        shell_html,
        router_options,
        realtime=realtime,
        ws_route=ws_route,
        events=event_registry,
        rate_limiter=rate_limiter,
    )
    app.include_router(router, prefix=norm_base if norm_base != "/" else "")
    if event_registry:
        app.state.layout_engine_events = event_registry
    if realtime and hub:
        app.state.layout_engine_realtime = hub
    if rate_limiter:
        app.state.layout_engine_rate_limiter = rate_limiter

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
    if realtime and hub and ws_route:
        hub.mount(app, ws_route)

        async def _start_realtime() -> None:  # noqa: D401
            await hub.start_publishers(realtime.publishers)

        async def _stop_realtime() -> None:  # noqa: D401
            await hub.stop_publishers()
            await hub.disconnect_all()

        app.add_event_handler("startup", _start_realtime)
        app.add_event_handler("shutdown", _stop_realtime)

    # Cleanup rate limiter on shutdown
    if rate_limiter:

        async def _stop_rate_limiter() -> None:  # noqa: D401
            await rate_limiter.stop_cleanup()

        app.add_event_handler("shutdown", _stop_rate_limiter)


def _create_layout_router(
    manifest_builder: ManifestBuilder,
    shell_html: str,
    router_options: RouterOptions,
    *,
    realtime: RealtimeOptions | None,
    ws_route: str | None,
    events: Mapping[str, UiEvent] | None,
    rate_limiter: InMemoryRateLimiter | None = None,
) -> APIRouter:
    router = APIRouter()
    event_registry = events or {}
    router.layout_engine_events = event_registry  # type: ignore[attr-defined]

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
        _inject_realtime_metadata(payload, realtime, ws_route)
        return JSONResponse(content=payload)

    if event_registry:

        @router.api_route(
            "/events/{event_id}",
            methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            response_class=JSONResponse,
        )
        async def handle_event(
            event_id: str,
            request: Request,
        ) -> Response:
            # Apply rate limiting if enabled
            if rate_limiter:
                await rate_limiter.check_rate_limit(request)

            event = event_registry.get(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Unknown event id")

            if request.method != event.method:
                raise HTTPException(
                    status_code=405,
                    detail=f"Method {request.method} not allowed for event {event.id}",
                )

            payload = {}
            if request.method in {"POST", "PUT", "PATCH"}:
                try:
                    payload = await request.json()
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(
                        f"Invalid JSON payload for event '{event_id}': {e}"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid JSON payload"
                    ) from e
            elif request.method == "GET":
                payload = dict(request.query_params)

            # Validate payload against schema if provided
            if event.payload_schema:
                validate_event_payload(event_id, payload, event.payload_schema)

            # Execute event handler with error handling
            try:
                handler_output = event.handler(request, payload)
                if inspect.isawaitable(handler_output):
                    handler_output = await handler_output

                result: UiEventResult
                if isinstance(handler_output, UiEventResult):
                    result = handler_output
                elif handler_output is None:
                    result = UiEventResult()
                elif isinstance(handler_output, Mapping):
                    result = UiEventResult(body=handler_output)
                else:
                    # Handler returned invalid type
                    logger.error(
                        f"Event handler '{event_id}' returned invalid type: "
                        f"{type(handler_output)!r}"
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Event handler returned invalid response type"
                    )

            except HTTPException:
                # Re-raise HTTP exceptions (already handled)
                raise
            except Exception as e:
                # Log handler exceptions with context
                logger.error(
                    f"Event handler '{event_id}' failed",
                    extra={
                        "event_id": event_id,
                        "method": request.method,
                        "client": str(request.client) if request.client else "unknown",
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                    exc_info=True
                )
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error while processing event"
                )

            # Broadcast to WebSocket if configured
            hub = getattr(request.app.state, "layout_engine_realtime", None)
            if hub and result.channel and result.payload:
                try:
                    await hub.broadcast(result.channel, result.payload)
                except Exception as e:
                    # Log broadcast failures but don't fail the request
                    logger.error(
                        f"Failed to broadcast event '{event_id}' to channel "
                        f"'{result.channel}': {e}",
                        exc_info=True
                    )

            return JSONResponse(
                content=result.http_body(),
                status_code=result.status_code,
                headers=result.headers,
            )

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


def _normalize_events(
    events: Sequence[UiEvent] | Mapping[str, UiEvent] | None,
) -> dict[str, UiEvent]:
    if not events:
        return {}
    registry: dict[str, UiEvent] = {}
    if isinstance(events, Mapping):
        items = events.values()
    else:
        items = events
    for entry in items:
        if not isinstance(entry, UiEvent):
            raise TypeError(
                "events collection must contain UiEvent instances; "
                f"received {type(entry)!r}"
            )
        event_id = entry.id
        if not event_id:
            raise ValueError("UiEvent.id must be a non-empty string")
        if event_id in registry:
            raise ValueError(f"Duplicate UiEvent id detected: {event_id!r}")
        registry[event_id] = entry
    return registry


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
        [binding.as_payload() for binding in bindings], separators=(",", ":")
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
