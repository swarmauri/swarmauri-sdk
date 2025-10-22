# Layout Engine Vue Runtime

Thin Vue wrapper for rendering Layout Engine manifests without custom dashboard
code. The runtime ships with default atom renderers, manifest/state handling,
theme support, and optional realtime event bridging.

## Installation

```bash
# Python package (includes the runtime bundle)
pip install layout-engine-atoms

# Optional: rebuild the bundled assets (requires Node + npm)
./scripts/build_vue_runtime.sh
```

The build script runs inside `runtime/vue/client/` and emits production-ready ESM
and UMD bundles into `runtime/vue/client/dist/`. Wheels published to PyPI ship
prebuilt assets, so rebuilding is only needed when iterating locally.

## Quick Start

```python
from fastapi import FastAPI
from layout_engine_atoms.runtime.vue import create_layout_app
from my_project.manifest import build_manifest

app = FastAPI()
vue_app = create_layout_app(
    manifest_builder=build_manifest,
    mount_path="/dashboard",
)
app.mount("/dashboard", vue_app.asgi_app())
```

The helper returns a `ManifestApp` that serves:

- `manifest.json`
- `layout-engine-vue.es.js` and `layout-engine-vue.umd.js`
- Static CSS/assets from `dist/`

## Runtime Options

### `create_layout_app(...)`

```python
create_layout_app(
    manifest_builder,
    mount_path="/dashboard",
    catalog="vue",
    events=None,
    extra_headers=(),
)
```

- `manifest_builder`: callable returning a manifest (`dict` or `layout_engine.Manifest`)
- `mount_path`: base URL prefix to serve assets and manifest
- `catalog`: defaults to `"vue"` for atom presets; override if you provide a custom catalog
- `events`: pass a `ManifestEventsConfig` to enable websocket multiplexing
- `extra_headers`: iterable of `(header, value)` pairs appended to responses

### Client Controller

```javascript
import { createLayoutApp } from "/dashboard/layout-engine-vue.es.js";

const controller = createLayoutApp({
  target: "#app",
  manifestUrl: "/dashboard/manifest.json",
  components: {
    "viz:metric:kpi": CustomMetric,
  },
  fetchOptions: { credentials: "include" },
  initialPageId: "overview",
  events: true,
  onReady: (manifest) => console.log("loaded", manifest.version),
  onError: (err) => console.error("manifest failed", err),
  plugins: [
    {
      beforeRender(ctx) {
        console.log("before render", ctx.view.page?.id);
      },
      afterUpdate(ctx) {
        console.log("tiles", ctx.view.tiles.length);
      },
    },
  ],
});
```

Controller helpers:

- `controller.refresh()` – refetch the manifest
- `controller.setPage(pageId)` – navigate to another page
- `controller.setTheme(patch, options)` – adjust runtime theme tokens or styles
- `controller.registerAtomRenderer(role, component)` – register/override atoms
- `controller.sendEvent(payload)` – publish client events during an active websocket session
- `controller.events.state` – reactive status of the websocket bridge

Passing `events: true` enables the default websocket bridge. Use an object for
fine-grained control:

```javascript
events: {
  url: "wss://demo.example.com/dashboard/events",
  autoReconnect: true,
  reconnectDelay: 2000,
  protocols: ["json.v1"],
}
```

## Theming

`controller.setTheme` accepts either a partial patch or `{ reset: true }` to
replace the current theme. Tokens are injected as CSS variables (`--le-*`) on
`<html>` and `<body>`.

```javascript
controller.setTheme({
  tokens: {
    "color-surface": "#f4fffb",
    "color-text-primary": "#113a3a",
  },
  style: {
    background: "linear-gradient(135deg, #f4fffb 0%, #d3f8f2 65%)",
  },
});
```

The default token system follows Swiss grid conventions; refer to
`docs/swiss_grid_theme.md` for a detailed mapping.

## Server-side Events

Use `ManifestEventsConfig` to subscribe clients to topics and respond to
messages:

```python
from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.vue import ManifestEventsConfig

bus = InProcEventBus()
router = EventRouter(bus)

events = ManifestEventsConfig(
    bus=bus,
    router=router,
    topics=("manifest",),
    on_client_event=lambda payload, ws: True,
)

vue_app = create_layout_app(
    manifest_builder=build_manifest,
    mount_path="/dashboard",
    events=events,
)
```

## Development Playground

The runtime ships with an inline Vite playground (`runtime/vue/client/src/main.js`).
Launch it with:

```bash
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client dev
```

This loads the example manifest and lets you iterate on atom renderers or theme
tokens with hot module replacement.
