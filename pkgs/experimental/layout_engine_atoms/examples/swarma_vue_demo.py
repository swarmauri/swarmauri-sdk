from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI

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
from layout_engine.atoms import AtomRegistry

from layout_engine_atoms.catalog.swarma_vue import build_registry as build_vue_registry
from layout_engine_atoms.runtime.vue import create_layout_app, load_client_assets

REPO_ROOT = Path(__file__).resolve().parents[4]
SWARMAKIT_ROOT = REPO_ROOT / "pkgs" / "experimental" / "swarmakit"


def build_manifest() -> dict:
    registry: AtomRegistry = build_vue_registry()

    tiles = [
        TileSpec(
            id="cta_primary",
            role="ui:button:primary:vue",
            props={
                "label": "View Dashboard",
                "type": "primary",
            },
        ),
        TileSpec(
            id="cta_secondary",
            role="ui:button:primary:vue",
            props={
                "label": "Export Report",
                "type": "secondary",
                "disabled": False,
            },
        ),
    ]

    layout = table(
        row(
            col(block("cta_primary"), size=SizeToken.m),
            col(block("cta_secondary"), size=SizeToken.m),
        )
    )

    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=960, height=540),
        tiles,
        atoms_registry=registry,
        version="2025.01",
    )
    return manifest


def _read_swarmakit_asset(relative_path: str) -> bytes:
    asset_path = SWARMAKIT_ROOT / relative_path
    if not asset_path.exists():
        raise FileNotFoundError(
            f"Expected SwarmaKit asset at {asset_path!s}. "
            "Run `pnpm --filter @swarmakit/vue build` in pkgs/experimental/swarmakit."
        )
    return asset_path.read_bytes()


def build_static_assets() -> dict[str, bytes]:
    assets = dict(load_client_assets())

    # Import map so the browser can resolve SwarmaKit modules and Vue runtime.
    import_map = {
        "imports": {
            "vue": "https://unpkg.com/vue@3/dist/vue.esm-browser.js",
            "@swarmakit/vue": "./vendor/swarma/vue.js",
        }
    }
    import_map_script = json.dumps(import_map, indent=2)

    # Include SwarmaKit's compiled bundle + stylesheet for the runtime demo.
    assets["vendor/swarma/vue.js"] = _read_swarmakit_asset("libs/vue/dist/vue.js")
    style_link_tag = ""
    style_path = SWARMAKIT_ROOT / "libs/vue/dist/style.css"
    if style_path.exists():
        assets["vendor/swarma/style.css"] = style_path.read_bytes()
        style_link_tag = '<link rel="stylesheet" href="./vendor/swarma/style.css" />'

    demo_script = """
import { createLayoutApp } from "./layout-engine-vue.es.js";
import { defineComponent, h } from "vue";
import { Button as SwarmaButton } from "@swarmakit/vue";

const SwarmaButtonAtom = defineComponent({
  name: "SwarmaButtonAtom",
  props: {
    tile: { type: Object, required: true },
  },
  setup(props) {
    const label = () => props.tile?.props?.label ?? "Call to Action";
    const type = () => props.tile?.props?.type ?? "primary";
    const disabled = () => props.tile?.props?.disabled ?? false;

    return () =>
      h(
        SwarmaButton,
        {
          type: type(),
          disabled: disabled(),
        },
        {
          default: () => label(),
        },
      );
  },
});

const controller = createLayoutApp({
  target: "#app",
  manifestUrl: "./manifest.json",
    components: {
    "ui:button:primary:vue": SwarmaButtonAtom,
  },
  onReady(manifest) {
    console.log("[demo] manifest ready", manifest.version);
  },
  onError(error) {
    console.error("[demo] manifest error", error);
  },
});

window.SwarmaKitVueDemo = controller;
"""

    assets["swarma-vue-demo.js"] = demo_script.strip().encode("utf-8")

    index_html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>SwarmaKit Vue Atom Demo</title>
    <link rel="stylesheet" href="./src/styles.css" />
    {style_link_tag}
    <script>
    (function() {{
      const globalProcess = globalThis.process || {{}};
      globalProcess.env = globalProcess.env || {{}};
      if (!("NODE_ENV" in globalProcess.env)) {{
        globalProcess.env.NODE_ENV = "production";
      }}
      globalThis.process = globalProcess;
      if (typeof window !== "undefined") {{
        window.process = globalProcess;
      }}
      var process = globalProcess;
    }})();
    </script>
    <script type="importmap">
    {import_map_script}
    </script>
    <style>
      body {{
        margin: 0;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #0f172a;
        color: #e2e8f0;
      }}
      .demo-shell {{
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 32px 64px;
      }}
      .demo-shell h1 {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
      }}
      .demo-shell p {{
        color: #94a3b8;
        margin-bottom: 1.5rem;
      }}
      #app {{
        border-radius: 16px;
        background: #1e293b;
        padding: 32px;
        min-height: 320px;
      }}
    </style>
  </head>
  <body>
    <div class="demo-shell">
      <h1>SwarmaKit Vue Button via Layout Engine</h1>
      <p>
        The manifest below renders the <code>ui:button:primary:vue</code> atom using the SwarmaKit bundle.
      </p>
      <div id="app">Loading dashboard…</div>
    </div>
    <script type="module" src="./swarma-vue-demo.js"></script>
  </body>
</html>
"""

    assets["index.html"] = index_html.strip().encode("utf-8")
    return assets


def create_app() -> FastAPI:
    app = FastAPI(title="SwarmaKit Vue Demo")

    vue_app = create_layout_app(
        manifest_builder=build_manifest,
        mount_path="/swarma-vue",
        static_assets=build_static_assets(),
    )
    app.mount("/swarma-vue", vue_app.asgi_app())
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8060)
