# layout-engine-atoms · Svelte Runtime (Work in Progress)

This directory houses the Svelte-facing wrapper for the shared layout-engine
runtime. The goal is to expose the same primitives delivered by the Vue thin
layer while reusing the platform-neutral logic under `runtime/core/`.

## Shared runtime dependencies

The Svelte adapter will import the following helpers from `runtime/core/`:

- `createRuntimeState` for manifest fetching, view derivation, and state
  subscriptions.
- `createThemeController`, `mergeTheme`, and `SWISS_GRID_THEME` to manage theme
  tokens and runtime styling overrides.
- `createDocumentThemeApplier` to synchronise CSS custom properties with the
  document root when the runtime mounts.
- `manifestFromPayload` and `resolveManifestPage` to hydrate manifests from
  payloads and select active pages.
- `computeGridPlacement` to derive per-tile CSS grid positions.
- `createEventBridge` and `deriveEventsUrl` for optional WebSocket-powered
  manifest updates.
- `createPluginManager` to support before/after render hooks shared with the Vue
  runtime.
- `deepMerge`, `isPlainObject`, and other utilities for safe data handling.
- Formatters (`formatPrimaryValue`, `formatDelta`, `markdownToHtml`,
  `normalizeBarSeries`, etc.) used by atom renderers.

## Planned module layout

```
runtime/
  svelte/
    __init__.py                # Python shim for manifest/event helpers (parity with Vue)
    README.md                  # You are here
    client/
      package.json             # Svelte + Vite toolchain metadata
      vite.config.js           # Bundler entry configuring Svelte plugin
      README.md                # Runtime usage and development docs
      src/
        runtime.js             # Public factory exporting createLayoutApp, DashboardApp, TileHost
        runtime-core.js        # createRuntime implementation that wires core helpers into Svelte
        atom-renderers.js      # Factory returning renderers backed by Svelte components
        context.js             # Context key helpers for layout state/event dispatch
        styles.css             # Base dashboard styling, reused by demo + host apps
        components/
          DashboardApp.svelte  # Top-level dashboard composition component
          TileHost.svelte      # Responsible for rendering individual tiles with slot props
          LayoutProvider.svelte# Provides context, theme bindings, and lifecycle wiring
        demo/
          main.js              # (Optional) playground entry that mounts the dashboard for testing
          App.svelte           # Example usage stub exercising key runtime APIs
```

Each stub file will be filled in future commits. The goal for now is to provide
structure and document responsibilities so implementation work can be split
cleanly.

