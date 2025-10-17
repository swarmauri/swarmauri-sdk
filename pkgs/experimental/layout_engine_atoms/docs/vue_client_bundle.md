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

## Developing locally

Use Vite's dev server to iterate on the client bundle with hot reload:

```bash
npm run --prefix pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client dev
```

The server opens `index.html`, which mounts the wrapper against the packaged
manifest in `examples/vue/`.
