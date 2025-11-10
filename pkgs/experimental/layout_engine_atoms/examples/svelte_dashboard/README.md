# Svelte Layout Engine Demo

Quick FastAPI example that mounts the Svelte runtime (`mount_svelte_app`) to show
parity with the Vue multi-page demo, including realtime channel updates.

## Run

```bash
uv run --directory pkgs/experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn layout_engine_atoms.examples.svelte_dashboard.server:app --reload
```

Visit `http://127.0.0.1:8000/` to see the dashboard and watch the hero pulse tile
update via websocket events.
