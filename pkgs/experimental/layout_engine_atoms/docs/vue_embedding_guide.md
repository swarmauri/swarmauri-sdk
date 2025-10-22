# Embedding the Vue Runtime

This guide covers the recommended workflows for using
`layout_engine_atoms.runtime.vue` inside a fresh Vue application, regardless of
whether you render on the client only or perform server-side rendering (SSR).

## 1. Install and build once

```bash
# install runtime dependencies
npm install --save layout-engine-atoms

# optional: rebuild the client bundle (ESM + UMD) if you plan to publish
./scripts/build_vue_runtime.sh  # from the repository root
```

> The published package already ships the `/dist` artifacts under
> `layout_engine_atoms/runtime/vue/client/dist/`. Rebuilding is only needed when
> customizing the wrapper or bundling it into your own npm package.

## 2. Client-side (CSR) usage

```javascript
import { createLayoutApp } from "layout_engine_atoms/runtime/vue/client/dist/layout-engine-vue.es.js";

const controller = createLayoutApp({
  manifestUrl: "/dashboard/manifest.json",
  target: "#app",
  events: true, // opt into realtime websocket bridge
});

controller.registerAtomRenderer("viz:metric:kpi", MyMetricComponent);
```

- Mount the wrapper into an empty `<div id="app"></div>` element.
- Use `controller.sendEvent(...)` to publish client events through the websocket.
- Call `controller.setTheme(...)` to tune spacing/density using the exposed
  design tokens.

## 3. Server-side rendering (SSR)

When hydrating on the server, render a shell HTML page that matches the slot
layout, then hydrate with the wrapper:

1. Use `create_layout_app` (or `ManifestApp` directly) to serve:
   - `/dashboard/manifest.json`
   - `/dashboard/index.html` (the shell or SSR output)
   - `/dashboard/layout-engine-vue.es.js` (the ESM bundle)
2. On the server, emit something similar to:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Dashboard</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module">
      import { createLayoutApp } from "/dashboard/layout-engine-vue.es.js";
      createLayoutApp({ manifestUrl: "/dashboard/manifest.json", target: "#app" });
    </script>
  </body>
</html>
```

For full SSR (rendering Vue components server-side) integrate the wrapper inside
your existing Vue SSR pipeline and ensure the manifest JSON is already fetched
before rendering. The returned controller still supports runtime refresh and
event streaming after hydration.

## 4. Publishing guidance

- **npm distribution** – publish your package after running the local Vite
  build so `dist/` contains both ESM (`layout-engine-vue.es.js`) and UMD
  (`layout-engine-vue.umd.js`) outputs. Consumers can import from the ESM path
  directly.
- **Python-only distribution** – when shipping via PyPI, run
  `npm run build` once; the generated `dist/` files are included in the wheel so
  `ManifestApp` can serve the assets without requiring Node at runtime.
- **Custom bundlers** – if embedding inside a larger SPA, treat the ESM bundle
  as any other library import. The wrapper carries no global state and respects
  tree-shaking via ES modules.

## 5. Realtime considerations

- `events: true` automatically derives the websocket URL (`/events` next to the
  manifest) and reconnects with backoff.
- Override `events` with `{ url, autoReconnect, onManifest, onMessage }` for
  advanced routing.
- Server-side `ManifestEventsConfig` hooks (`on_client_event`, `on_connect`)
  let you manage acknowledgements, update tiles in place, or broadcast analytics
  signals.

## 6. Development workflow

```bash
# Run the local wrapper playground with HMR
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client dev

# Rebuild the production bundles
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client build
```

The Vite dev server proxies requests to the packaged demo manifest so you can
iterate on custom atom renderers or theming before shipping them downstream.
