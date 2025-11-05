# @swarmakit/layout-engine-vue

> Thin Vue wrapper for Layout Engine manifests and SwarmaKit atoms.

## Installation

```bash
pnpm add @swarmakit/layout-engine-vue
```

Peer dependencies:

```bash
pnpm add vue @swarmakit/vue
```

## Server Quickstart (Python)

```python
from layout_engine import (
    AtomRegistry,
    AtomSpec,
    LayoutCompiler,
    LayoutManifest,
    ManifestBuilder,
    TileSpec,
    Viewport,
)
from layout_engine.grid.spec import GridSpec, GridTrack, GridTile
from layout_engine.core.size import Size

atoms = AtomRegistry()
atoms.register(
    AtomSpec(
        role="swarmakit:vue:hero",
        module="@swarmakit/vue",
        export="HeroCard",
        defaults={"size": "md"},
        family="swarmakit",
    )
)

compiler = LayoutCompiler()
viewport = Viewport(width=1280, height=720)
grid = GridSpec(columns=[GridTrack(size=Size(1, "fr"))])
placements = [GridTile(tile_id="hero", col=0, row=0)]
frames = compiler.frames(grid, viewport, placements)

view_model = compiler.view_model(
    grid,
    viewport,
    frames,
    [TileSpec(id="hero", role="swarmakit:vue:hero", props={"title": "Welcome"})],
    atoms_registry=atoms,
    channels=[{"id": "ui.events", "scope": "page", "topic": "page:{page_id}:ui"}],
    ws_routes=[{"path": "/ws/ui", "channels": ["ui.events"]}],
)

manifest = ManifestBuilder().build(view_model)
# expose `manifest` via FastAPI/Flask etc. at /api/manifest.json
```

## Vue Quickstart

```ts
// main.ts
import { createApp } from "vue";
import App from "./App.vue";
import { createLayoutEngineApp } from "@swarmakit/layout-engine-vue";

async function bootstrap() {
  const engine = await createLayoutEngineApp({
    manifestUrl: "/api/manifest.json",
    muxUrl: "ws://localhost:8765/ws/ui",
  });

  const vueApp = createApp(App, { manifest: engine.manifest });
  vueApp.use(engine.plugin);
  vueApp.mount("#app");
}

bootstrap();
```

```vue
<!-- App.vue -->
<template>
  <LayoutEngineShell>
    <template #default="{ site }">
      <nav class="nav">
        <LayoutEngineNavLink
          v-for="page in site.pages"
          :key="page.id"
          :page-id="page.id"
        >
          {{ page.title ?? page.id }}
        </LayoutEngineNavLink>
      </nav>
    </template>
  </LayoutEngineShell>
</template>
```

## Commands

```bash
pnpm install
pnpm dev      # start Vite playground (configure separately)
pnpm build    # build library bundles
pnpm test     # run Vitest suite
```

## Testing

Vitest example test (`tests/loader.spec.ts`) validates manifest hydration and component caching. Add
more coverage as runtime features expand (e.g. WebSocket mux integration).

---

MIT © Swarmauri Labs
