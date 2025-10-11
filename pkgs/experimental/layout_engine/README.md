![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/dm/layout-engine" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine.svg"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/pyversions/layout-engine" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/l/layout-engine" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/layout-engine/">
        <img src="https://img.shields.io/pypi/v/layout-engine?label=layout-engine&color=green" alt="PyPI - layout-engine"/></a>
</p>

---

# Layout Engine (Core)

`layout-engine` is a Swiss Grid design inspired, format-agnostic rendering engine that powers Server-Side Rendering (SSR), Static Site Generation (SSG), and offline exports from a unified component model. The package provides strongly-typed contracts for sites, pages, grids, tiles, and component registries so downstream applications can orchestrate layouts without being tied to a specific UI framework.

> **Python compatibility:** officially supports Python 3.10, 3.11, and 3.12.

## Features

- **Contract-driven architecture** – abstract base classes define the interfaces for rendering, exporting, and serving layout primitives.
- **Atomic component & micro-frontend registries** – manage SSR-ready components and remote module manifests with predictable defaults.
- **Format agnostic targets** – render HTML, SVG, PDF, and code artifacts using interchangeable exporters.
- **Extensible site composition** – compose grids, tiles, and slots declaratively with Pydantic specs for validation and serialization.
- **Optional realtime bridge** – opt into FastAPI, Uvicorn, and WebSocket extras for live preview or event streaming.

## Installation

Choose the workflow that matches your tooling. Extras are available for realtime server capabilities (`server`) and PDF generation (`pdf`).

```bash
# uv
uv add layout-engine
uv add layout-engine[server]  # for FastAPI/WebSocket extras
uv add layout-engine[pdf]     # for Playwright-powered exports

# pip
pip install layout-engine
pip install "layout-engine[server]"
pip install "layout-engine[pdf]"
```

## Quick Start

```python
from layout_engine import (
    ComponentRegistry,
    ComponentSpec,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.targets.media import HtmlExporter

components = ComponentRegistry()
components.register(ComponentSpec(role="stat", module="@demo/metric"))

tiles = [
    TileSpec(id="stat_revenue", role="stat", props={"label": "Revenue", "value": "$1.2M"}),
    TileSpec(id="stat_growth", role="stat", props={"label": "Growth", "value": "18%"}),
]

layout = table(
    row(
        col(block("stat_revenue"), size=SizeToken.m),
        col(block("stat_growth"), size=SizeToken.m),
    )
)

manifest = quick_manifest_from_table(
    layout,
    Viewport(width=960, height=540),
    tiles,
    components_registry=components,
)

HtmlExporter(title="Stats Overview").export(manifest, out="stats.html")
```

The manifest merges component defaults with any props provided on `TileSpec`
instances, so runtime components receive fully-prepared payloads.

### Examples

- [`examples/basic_usage.py`](./examples/basic_usage.py) – minimal quick-start
  script that writes a manifest JSON file and exports an HTML preview.
- [`examples/dashboard.py`](./examples/dashboard.py) – larger end-to-end demo
  showcasing multiple roles and a custom theme.

Run either script with:

```bash
uv run --directory experimental/layout_engine --package layout-engine python examples/basic_usage.py
uv run --directory experimental/layout_engine --package layout-engine python examples/dashboard.py
```

Both scripts print their output locations so you can open the generated
artifacts directly from the repository.

## Core Concepts

- **First-class objects** – `site`, `page`, `slot`, `grid`, `tile`, `component`, and `remote` provide the building blocks for any layout.
- **Contracts** – objects expose `.render(...)`, `.export(...)`, and optional `.server(...)` methods to support SSR, SSG, and service endpoints.
- **Registries** – manage atomic component defaults and micro-frontend remotes with predictable merge semantics.
- **Site-aware routing helpers** – `layout_engine.targets.SiteRouter` produces SSR HTML shells, manifest JSON payloads, and ESM
  import maps you can bind directly to FastAPI, Starlette, or any HTTP framework route handlers.

### Serving manifests and import maps

`SiteRouter` centralizes the endpoints required by single-page and multi-page applications. Use
`SiteRouter.manifest_json(...)` to return the manifest for a page, and
`SiteRouter.import_map(...)` to build an import map from a `RemoteRegistry`. Because the router is
framework-agnostic, you can wire these helpers into whichever ASGI/WSGI stack you prefer without
additional adapters.

## End-to-end Vue SPA + MPA integration

The following walkthrough shows how to create a Vue codebase that consumes both single-page and
multi-page manifests generated by `layout-engine`, serves an import-map aware shell, reacts to query
parameters, and streams tile-level events over a multiplexed WebSocket transport.

### 1. Compose registries and site metadata

Start by defining the component registry (for local role → module mappings) and the remote registry
that powers the import map consumed by Vue's module loader. Defaults defined on each component are
merged with tile props every time a manifest is built, so downstream components always receive a
complete prop payload.

```python
from layout_engine import ComponentRegistry, ComponentSpec
from layout_engine.mfe.default import RemoteRegistry
from layout_engine.mfe.spec import Remote
from layout_engine.site.spec import PageSpec, SiteSpec, SlotSpec

components = ComponentRegistry()
components.register(
    ComponentSpec(
        role="dashboard.hero",
        module="@layout-app/components",
        export="HeroCard",
        version="2.1.0",
        defaults={"accent": "indigo", "density": "comfortable"},
    )
)
components.register(
    ComponentSpec(
        role="catalog.item",
        module="@layout-app/components",
        export="CatalogTile",
        defaults={"showPrice": True, "badgeStyle": "pill"},
    )
)

remotes = RemoteRegistry(
    (
        Remote(
            id="spa-shell",
            framework="vue",
            entry="https://cdn.example.com/spa/entry.js",
            exposed="./App",
        ),
        Remote(
            id="mpa-shell",
            framework="vue",
            entry="https://cdn.example.com/mpa/entry.js",
            exposed="./Page",
        ),
    )
)

site = SiteSpec(
    base_path="/",
    pages=(
        PageSpec(
            id="spa-dashboard",
            route="/",
            title="Realtime Dashboard",
            slots=(SlotSpec(name="root", role="dashboard.hero", remote="spa-shell"),),
            page_vm={"state": {"filters": {"status": "active"}}},
        ),
        PageSpec(
            id="catalog-list",
            route="/catalog",
            title="Product Catalog",
            slots=(SlotSpec(name="root", role="catalog.item", remote="mpa-shell"),),
        ),
        PageSpec(
            id="catalog-detail",
            route="/catalog/:item_id",
            title="Product Detail",
            slots=(SlotSpec(name="root", role="catalog.item", remote="mpa-shell"),),
        ),
    ),
)
```

### 2. Build manifests that react to SPA and MPA context

Use the authoring DSL to convert structured layouts into manifests. The manifest builder receives a
`PageSpec` plus a context assembled by `SiteRouter`, which includes route params, query parameters,
and any `page_vm` defaults. This is the hook for computing stateful props (selected items, applied
filters, etc.) before merging with the registry defaults.

```python
from typing import Mapping, Any

from layout_engine import (
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.manifest.spec import Manifest

catalog_source = {
    "items": [
        {"id": "sku-001", "name": "Synthwave Jacket", "price": 180},
        {"id": "sku-002", "name": "Neon Sneakers", "price": 120},
        {"id": "sku-003", "name": "Retro Shades", "price": 60},
    ]
}


def build_manifest(page: PageSpec, ctx: Mapping[str, Any]) -> Manifest:
    route = ctx["route"]
    query = route.get("query", {})
    params = route.get("params", {})
    base_state = dict(ctx.get("state", {}))
    # Merge defaults with incoming query params to derive view state
    active_filters = {
        **base_state.get("filters", {}),
        **{k: v for k, v in query.items() if k in {"status", "search", "page"}},
    }

    if page.id == "spa-dashboard":
        tiles = [
            TileSpec(
                id="hero",
                role="dashboard.hero",
                props={
                    "filters": active_filters,
                    "headline": "Realtime sales",
                    "kpi": {"value": "$1.8M", "trend": +12},
                },
            ),
        ]
    elif page.id == "catalog-list":
        # Apply search filter from query params for list rendering
        search_term = (query.get("search") or "").lower()
        filtered = [
            item
            for item in catalog_source["items"]
            if search_term in item["name"].lower()
        ]
        tiles = [
            TileSpec(
                id=item["id"],
                role="catalog.item",
                props={
                    "itemId": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "isActive": False,
                },
            )
            for item in filtered
        ]
    else:
        # Detail view resolves the selected item id from params
        item_id = params.get("item_id")
        item = next(
            (item for item in catalog_source["items"] if item["id"] == item_id),
            None,
        )
        tiles = [
            TileSpec(
                id="detail",
                role="catalog.item",
                props={
                    "itemId": item_id,
                    "name": item.get("name") if item else "Missing",
                    "price": item.get("price") if item else 0,
                    "isActive": True,
                },
            )
        ]

    layout = table(
        row(
            *(col(block(tile.id), size=SizeToken.l) for tile in tiles)
        )
    )
    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1440, height=900),
        tiles,
        components_registry=components,
    )
    return manifest
```

The snippet shows how component defaults (`showPrice`, `badgeStyle`) are merged with dynamic props
(`isActive`, `filters`) before the manifest reaches the client. State changes (for example selecting
an item or refining a search query) happen entirely in the context step—no Vue-specific logic is
required on the server to keep props synchronized.

### 3. Serve shells, manifests, and import maps with `SiteRouter`

Bind the manifest builder to a `SiteRouter` so both SPA and MPA routes can be served from the same
FastAPI (or Starlette) application. The SPA fetches a single manifest keyed by `PageSpec`, whereas
the MPA endpoints use `manifest_json_for_path` so each HTML page can request its own manifest.

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from layout_engine.site.default import bind_page_builder
from layout_engine.targets.webgui.router import SiteRouter

router = SiteRouter(site=site, page_manifest_fn=bind_page_builder(build_manifest))

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def spa_shell() -> str:
    return router.render_shell(site.pages[0])


@app.get("/spa/manifest.json")
async def spa_manifest(request: Request) -> JSONResponse:
    data = router.manifest_json(
        site.pages[0],
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


@app.get("/catalog", response_class=HTMLResponse)
async def catalog_shell() -> str:
    page = site.pages[1]
    return router.render_shell(page)


@app.get("/catalog/manifest.json")
async def catalog_manifest(request: Request) -> JSONResponse:
    data = router.manifest_json_for_path(
        "/catalog",
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


@app.get("/catalog/{item_id}", response_class=HTMLResponse)
async def catalog_detail_shell(item_id: str) -> str:
    page = site.pages[2]
    return router.render_shell(page, params={"item_id": item_id})


@app.get("/catalog/{item_id}/manifest.json")
async def catalog_detail_manifest(item_id: str, request: Request) -> JSONResponse:
    data = router.manifest_json_for_path(
        f"/catalog/{item_id}",
        query=dict(request.query_params),
    )
    return JSONResponse(content=data)


@app.get("/import-map.json")
async def import_map() -> JSONResponse:
    return JSONResponse(router.import_map(remotes))
```

This wiring enables:

- **SPA manifest** – `GET /spa/manifest.json?status=paused` updates dashboard props while keeping a
  single HTML shell.
- **MPA manifests** – each catalog page calls `/catalog/…/manifest.json` so static HTML routes can
  hydrate independently, while still sharing component defaults from the registry.
- **Import maps** – Vue clients can consume the generated map before calling `createApp` to ensure
  micro-frontend remotes resolve correctly.

### 4. Vue client consumption with query params and navigation

In the Vue SPA entry point, request the manifest and import map, register slots, and watch the URL's
query parameters to re-fetch manifests whenever filters change. For the MPA flows, the same manifest
loader runs on each page load, so a full navigation to `/catalog/sku-001` will resolve the detail
manifest that already includes the requested item.

```ts
// spa/main.ts
import { createApp, ref } from "vue";
import App from "./App.vue";

async function loadManifest(endpoint: string, query: URLSearchParams) {
  const res = await fetch(`${endpoint}?${query.toString()}`);
  return res.json();
}

async function bootstrap() {
  const importMap = await (await fetch("/import-map.json")).json();
  const script = document.createElement("script");
  script.type = "importmap";
  script.textContent = JSON.stringify(importMap);
  document.head.appendChild(script);

  const query = new URLSearchParams(window.location.search);
  const manifest = ref(await loadManifest("/spa/manifest.json", query));

  const app = createApp(App, { manifest });
  app.mount("#app");

  window.addEventListener("popstate", async () => {
    const nextQuery = new URLSearchParams(window.location.search);
    manifest.value = await loadManifest("/spa/manifest.json", nextQuery);
  });
}

bootstrap();
```

MPA pages perform the same fetch using their page-specific manifest endpoint, so the detail view can
call `loadManifest(`/catalog/${itemId}/manifest.json`, new URLSearchParams(location.search))` and the
server will deliver props for the requested `itemId`.

### 5. Event handling with multiplexed WebSockets

Install the optional server extras (`layout-engine[server]`) plus the WebSocket JSON-RPC transport
(`swarmauri-transport-wsjsonrpcmux`). The transport acts as the mux that fans events in/out of the
`layout_engine.events` router, giving Vue components a consistent channel for publishing or
subscribing to tile state changes. The mux is intentionally **shared by the entire site**—we do not
open a dedicated WebSocket per component. Instead, pages share a single JSON-RPC session that
correlates events by `{scope, page, slot, tile}`. This keeps connection counts predictable while
still letting individual atoms react to the subset of messages that match their manifest identity.

#### Server-side integration with the mux

Tie the mux lifecycle directly to your ASGI application startup so FastAPI (or Starlette) can expose
one process-wide connection hub. The mux simply delegates to an `EventRouter`, which wraps
`InProcEventBus` by default but can sit atop Redis, NATS, or any broker you prefer.

```python
import asyncio
from fastapi import FastAPI
from layout_engine.targets import SiteRouter
from swarmauri_transport_wsjsonrpcmux import WsJsonrpcMuxTransport
from layout_engine.events.ws import EventRouter, InProcEventBus

event_bus = InProcEventBus()
events = EventRouter(event_bus)
site_router = SiteRouter(site, components, remotes)


async def rpc_handler(method: str, params: dict):
    if method == "layout.publish":
        topic, delivered = events.dispatch(params)
        return {"topic": topic, "delivered": delivered}
    if method == "layout.subscribe":
        # In a production system forward the subscription request to a broker.
        # Here we eagerly replay the last event if available.
        topic = params["topic"]
        last = event_bus.last(topic)
        return {"topic": topic, "last": last}
    raise ValueError(f"Unknown method: {method}")


async def start_mux():
    transport = WsJsonrpcMuxTransport()
    transport.set_rpc_handler(rpc_handler)
    async with transport.server(host="0.0.0.0", port=8765):
        await asyncio.Future()


app = FastAPI()


@app.on_event("startup")
async def launch_mux():
    asyncio.create_task(start_mux())


app.get("/spa/manifest.json")(site_router.manifest_json)
app.get("/import-map.json")(site_router.import_map)
```

#### Vue atoms and remote modules on a shared mux

Vue clients connect once, then expose composition helpers so individual atoms (tiles, slots, or
remote wrappers) can subscribe without knowing about the socket. The helper below keeps a `Map` of
topic → callbacks and multiplexes inbound messages across all registered atoms.

```ts
type Listener = (payload: Record<string, any>) => void;

const socket = new WebSocket("ws://localhost:8765");
const listeners = new Map<string, Set<Listener>>();

socket.addEventListener("open", () => {
  socket.send(
    JSON.stringify({
      jsonrpc: "2.0",
      id: "init",
      method: "layout.subscribe",
      params: { topic: `site:${window.location.pathname}` },
    })
  );
});

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (!message.result?.topic) return;
  const topicListeners = listeners.get(message.result.topic);
  if (!topicListeners) return;
  topicListeners.forEach((fn) => fn(message.result.last ?? message.result.event));
});

function topicFor(scope: string, page: string, slot: string, tile?: string) {
  return `${scope}:${page}:${slot}${tile ? `:${tile}` : ""}`;
}

export function useLayoutEvents(scope: string, page: string, slot: string, tile?: string) {
  const topic = topicFor(scope, page, slot, tile);

  function publish(event: Record<string, any>) {
    socket.send(
      JSON.stringify({
        jsonrpc: "2.0",
        id: crypto.randomUUID(),
        method: "layout.publish",
        params: { scope, page, slot, tile, event },
      })
    );
  }

  function subscribe(listener: Listener) {
    if (!listeners.has(topic)) listeners.set(topic, new Set());
    listeners.get(topic)!.add(listener);
    return () => unsubscribe(listener);
  }

  function unsubscribe(listener: Listener) {
    listeners.get(topic)?.delete(listener);
    if (listeners.get(topic)?.size === 0) {
      listeners.delete(topic);
    }
  }

  return { publish, subscribe, unsubscribe };
}
```

Remote modules can now expose lightweight Vue atoms that bridge manifest props with the mux helper:

```vue
<!-- remotes/catalog/CatalogTile.vue -->
<template>
  <section @click="notifySelection" class="catalog-tile">
    <h3>{{ props.title }}</h3>
    <p>{{ props.description }}</p>
    <footer>{{ props.price }}</footer>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useLayoutEvents } from "@remotes/spa/events";

const props = defineProps<{
  id: string;
  slot: string;
  page: string;
  scope: string;
  title: string;
  description: string;
  price: string;
}>();

const { publish, subscribe } = useLayoutEvents(
  props.scope,
  props.page,
  props.slot,
  props.id,
);

const availability = ref<string | null>(null);

onMounted(() => {
  const listener = (event: Record<string, any>) => {
    if (event.type === "inventory.update") {
      availability.value = event.payload.status;
    }
  };

  const stop = subscribe(listener);
  onBeforeUnmount(() => stop());
});

function notifySelection() {
  publish({ type: "catalog.clicked", payload: { id: props.id } });
}
</script>
```

`CatalogTile` acts as a Vue atom inside a remote bundle while still respecting manifest-owned props
(`scope`, `page`, `slot`, `id`). Because every atom delegates to the shared mux, the connection count
remains constant regardless of how many components are rendered.

When components invoke `publish`, the event router validates the envelope, publishes to the topic
derived from `scope/page/slot/tile`, and any subscribed Vue atoms receive real-time updates.
Because `EventRouter.dispatch` accepts the same context that `SiteRouter` uses to build manifests,
the manifest props and WebSocket events stay aligned.

### 6. Putting it together

1. **Render shells** for each SPA/MPA page with `SiteRouter.render_shell(...)`.
2. **Serve manifests** via `manifest_json(...)` (SPA) and `manifest_json_for_path(...)` (MPA) so
   Vue can hydrate tiles with merged defaults, props, and query-derived state.
3. **Distribute import maps** generated from the `RemoteRegistry` so component modules resolve
   consistently across pages.
4. **Leverage context** (`route.params`, `route.query`, `page_vm`) inside the manifest builder to
   support list filtering, `item_id` lookups, and other state transitions.
5. **Stream events** through the muxed WebSocket transport to coordinate user interactions or live
   telemetry across SPA and MPA boundaries.

With these pieces in place, a Vue frontend can seamlessly navigate between SPA and MPA routes, reuse
the same manifest-driven layout definitions, and react instantly to query parameter changes or
WebSocket events without duplicating component metadata on the client.

## Development

```bash
uv sync --all-extras
uv run --directory experimental/layout_engine --package layout-engine ruff check .
uv run --directory experimental/layout_engine --package layout-engine pytest -q
```

## License

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.
