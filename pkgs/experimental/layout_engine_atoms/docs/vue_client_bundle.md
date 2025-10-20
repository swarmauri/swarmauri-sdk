# Vue Runtime Bundle Guide

This repository now ships the Vue thin wrapper assets under
`layout_engine_atoms.runtime.vue.client`. The code is authored as ESM modules and
can be bundled into distributable artifacts with Vite.

## Source layout

```
runtime/vue/client/
  ├── index.html        # demo entry that mounts the wrapper immediately
  ├── package.json      # local tooling dependencies (Vue, Vite)
  ├── vite.config.js    # builds the reusable library bundle
  └── src/
      ├── atom-renderers.js   # factory for Vue components used by manifest roles
      ├── atoms.js            # CDN bootstrap (used by the packaged demo)
      ├── runtime-core.js     # framework-agnostic runtime helpers
      ├── runtime.js          # library entry (imports from 'vue')
      └── main.js             # demo bootstrap (uses the CDN ESM build)
```

## Build commands

From the repository root:

```bash
# install dependencies (once per environment)
npm install --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client

# produce ESM + UMD bundles in client/dist/
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client build
```

The build writes `layout-engine-vue.es.js` and `layout-engine-vue.umd.js` into
`client/dist/`. `ManifestApp` automatically serves the `dist/` directory when it
exists, falling back to the raw source modules otherwise.

## Consuming the wrapper

After running the build step (or once the Python package ships prebuilt assets),
project code can import the thin wrapper as follows:

```javascript
import { createLayoutApp } from "layout_engine_atoms/runtime/vue/client/dist/layout-engine-vue.es.js";

const controller = createLayoutApp({
  target: "#app",
  manifestUrl: "/dashboard/manifest.json",
  onError(error) {
    console.error("manifest load failed", error);
  },
});
```

The returned controller exposes:

- `app` – the underlying Vue application instance
- `refresh()` – refetch the manifest
- `unmount()` – dispose of the mounted app
- `state` – reactive manifest state exposed by the dashboard component

### Custom atom renderers

Override or extend the default atom components by passing a `components` map:

```javascript
createLayoutApp({
  manifestUrl,
  components: {
    "viz:metric:kpi": MyMetricComponent,
    default: MyFallbackComponent,
  },
});
```

Unspecified roles fall back to the shipped presets. Supplying a `default`
renderer is optional; the packaged placeholder will be used when omitted.

### Fetch options and lifecycle hooks

You can pass `fetchOptions` (forwarded to `fetch`), `onError`, and `onReady`
callbacks to hook into the wrapper lifecycle:

```javascript
createLayoutApp({
  manifestUrl,
  fetchOptions: { credentials: "include" },
  onReady: (manifest) => console.log("loaded", manifest.version),
  onError: (err) => reportError(err),
});
```

### Realtime manifest streaming

Enable the realtime bridge by providing an `events` option. The runtime derives
the WebSocket endpoint from `manifestUrl` (defaulting to `/events` beside
`manifest.json`) and automatically reconnects when the transport drops.

```javascript
const controller = createLayoutApp({
  manifestUrl,
  events: {
    // Optional overrides
    url: "wss://demo.example.com/dashboard/events",
    autoReconnect: true,
    onManifest(manifest) {
      console.debug("streamed manifest", manifest.version);
    },
  },
});

// Send client events back to the server
controller.sendEvent({
  type: "site:navigate",
  request_id: crypto.randomUUID(),
  ts: new Date().toISOString(),
});
```

The controller exposes `controller.events.state` for connection status tracking,
plus helper methods `sendEvent`, `reconnectEvents`, and `disconnectEvents`.

### Server-side event handlers

`ManifestEventsConfig` accepts callbacks so the server can acknowledge or mutate
tile state when client events arrive. For example:

```python
from layout_engine.events.ws import EventRouter, InProcEventBus
from layout_engine_atoms.runtime.vue import ManifestApp, ManifestEventsConfig

bus = InProcEventBus()
router = EventRouter(bus)

async def on_client_event(payload, ws):
    # Acknowledge tile actions.
    if payload.get("topic") == "tiles" and payload.get("payload", {}).get("ack"):
        ack = payload["payload"]
        bus.publish("tiles/acks", {"tile_id": ack["tile_id"], "status": "ok"})
        return True

    # Apply a lightweight tile mutation.
    if payload.get("type") == "tile:patch" and payload.get("payload"):
        bus.publish(
            "manifest",
            {"type": "manifest.patch", "patch": {"tiles": payload["payload"]}},
            retain=True,
        )
        return True
    return False

app = ManifestApp(
    manifest_builder=build_manifest,
    mount_path="/dashboard",
    events=ManifestEventsConfig(
        bus=bus,
        router=router,
        topics=("manifest", "tiles/acks"),
        on_client_event=on_client_event,
    ),
)
```

Client code can stream acknowledgements or mutations through the bus and patch
local state without a full refresh:

```javascript
controller.sendEvent({
  topic: "tiles",
  payload: { ack: true, tile_id: "tile_ops" },
});

controller.sendEvent({
  type: "tile:patch",
  payload: [{ id: "tile_revenue", props: { value: 12_750_000 } }],
});
```

### Design tokens & theming

The runtime exposes design tokens as CSS custom properties prefixed with
`--le-`. Defaults cover Swiss-grid spacing, typography, and palette, and you can
override them via the `theme.tokens` option or by patching the theme after
mounting. Key tokens include:

- `color-surface`, `color-surface-elevated`, `color-text-primary`,
  `color-accent`
- `font-family-sans`, `font-size-base`, `font-size-xl`,
  `line-height-base`, `font-weight-semibold`
- `space-1…space-8`, `density` (scales spacing via multipliers)
- `grid-max-width`, `grid-column-min`, `viewport-padding-x`

```javascript
const controller = createLayoutApp({
  manifestUrl,
  theme: {
    tokens: {
      "color-surface": "#ffffff",
      "color-text-primary": "#1b1d29",
      "font-family-sans": "'General Sans', system-ui, sans-serif",
      "space-5": "1.25rem",
      density: 0.9,
    },
  },
});

// Adjust density at runtime
controller.setTheme({ tokens: { density: 1.1 } });
```

### Extension hooks

Runtime instances expose helpers for dynamic atom registration and plugin
lifecycle events:

- `controller.registerAtomRenderer(role, component)` and
  `controller.unregisterAtomRenderer(role)` adjust the renderer registry after
  mount. Registered components override the shipped presets immediately.
- `controller.registerPlugin(plugin)` adds a plugin object that can implement
  `beforeRender(ctx)` and `afterUpdate(ctx)` hooks; use
  `controller.unregisterPlugin(plugin)` or `controller.plugins.unregister(...)`
  to remove it.

```javascript
const controller = createLayoutApp({ manifestUrl, components: { custom: Foo } });

controller.registerAtomRenderer("viz:metric:kpi", MyLiveMetric);

controller.registerPlugin({
  beforeRender(ctx) {
    console.info("dashboard rendering", ctx.state.manifest?.version);
  },
  afterUpdate(ctx) {
    analytics.track("manifest:update", {
      tiles: ctx.view.tiles.length,
      status: ctx.events.status,
    });
  },
});
```

The plugin context (`ctx`) provides the reactive dashboard `state`, derived
`view`, `events` status, and helper methods (`refresh`, `setPage`, `setTheme`,
`sendEvent`).

### Page selection

Manifests that contain a `pages` collection can be controlled through
`initialPageId`, `pageId`, or via the returned controller:

```javascript
const controller = createLayoutApp({
  manifestUrl,
  initialPageId: "overview",
  resolvePage: (manifest, requested) => requested ?? manifest.pages?.[0]?.id,
  onPageChange: (pageId, page) => console.log("active page", pageId, page?.label),
});

// Switch pages at runtime
controller.setPage("details");
```

### Theme tokens and styling

Themes can be layered via `theme.className`, `theme.style`, and `theme.tokens`
(which map to CSS variables prefixed with `--le-`). You can also patch them
later using `controller.setTheme`:

```javascript
const controller = createLayoutApp({
  manifestUrl,
  theme: {
    className: "dashboard-theme",
    tokens: { accent: "#57b3ff" },
    style: { background: "#02030a" },
  },
});

// Merge additional overrides without remounting
controller.setTheme({ tokens: { accent: "#ff7a45" } });

// Replace the theme completely
controller.setTheme({ className: "light-theme" }, { replace: true });
```

## Developing locally

Use Vite's dev server to iterate on the client bundle with hot reload:

```bash
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client dev
```

The server opens `index.html`, which mounts the wrapper against the packaged
manifest in `examples/vue/`.
