# Vue Dashboard Example

This example shows how to serve a Layout Engine manifest with the bundled Vue
wrapper. It pairs the manifest generator with `layout_engine_atoms.runtime.vue`
so you can launch a working dashboard via ASGI/uvicorn.

## Files

- `generate_manifest.py` — constructs the manifest using `layout-engine` and the
  preset catalog.
- `dashboard.manifest.json` — optional snapshot written by the script above.
- `app.py` — creates a `ManifestApp` that serves the manifest and the Vue
  wrapper at `/dashboard`.

## Run the example

1. Optional: regenerate the manifest snapshot.

   ```bash
   uv run --directory pkgs/experimental/layout_engine_atoms --package layout-engine-atoms python examples/vue/generate_manifest.py
   ```

2. Start the ASGI server (requires `uvicorn`).

   ```bash
   uv run --directory pkgs/experimental/layout_engine_atoms --package layout-engine-atoms uvicorn layout_engine_atoms.examples.vue.app:app --reload
   ```

3. Open <http://127.0.0.1:8000/dashboard/> to view the dashboard. The Vue
   wrapper fetches `/dashboard/manifest.json`, renders tiles using the catalog
   components, and applies the grid from the manifest metadata.
