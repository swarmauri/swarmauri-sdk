# Vue Dashboard Example

This example shows how to consume a `layout-engine` manifest from a Vue 3
single-page application. It pairs the core DSL with the curated presets shipped
by `layout-engine-atoms`, then renders the resulting dashboard with Vue
components that understand each atom role.

## Files

- `generate_manifest.py` — builds `dashboard.manifest.json` using
  `layout-engine` + `layout-engine-atoms`.
- `dashboard.manifest.json` — sample manifest checked into the repo so the app
  works out of the box.
- `index.html` & `src/` — Vue front-end that fetches the manifest at runtime.

## Run the example

1. Regenerate the manifest (optional after edits):

   ```bash
   uv run --directory pkgs/experimental/layout_engine --package layout-engine python examples/vue-example/generate_manifest.py
   ```

2. Serve the folder locally (any static server works):

   ```bash
   cd pkgs/experimental/layout_engine/examples/vue-example
   python -m http.server 9000
   ```

3. Open <http://localhost:9000> in your browser. Vue bootstraps the dashboard,
   maps atom roles to Vue components, and lays out the tiles using the manifest's
   grid metadata.
