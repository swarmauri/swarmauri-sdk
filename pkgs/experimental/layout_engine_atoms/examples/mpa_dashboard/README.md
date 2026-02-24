# Multi-page Mission Control Demo

This example packages a styled, multi-page dashboard that showcases how
`layout_engine`, `layout_engine_atoms`, and the Vue runtime collaborate.
Each route returns a curated manifest composed from the SwarmaKit atom
catalogue and rendered through the prebuilt layout engine Vue shell.

## What you get

- A FastAPI server that mounts the layout engine Vue runtime assets.
- Three demo manifests (`overview`, `operations`, `revenue`) with rich props,
  consistent theming, and per-page metadata.
- Classic MPA navigation: each link loads a route-specific manifest while
  keeping the authored shell experience cohesive.

## Running the demo

```bash
# from repository root
uv run --directory pkgs/experimental/layout_engine_atoms \
  --package layout-engine-atoms \
  uvicorn layout_engine_atoms.examples.mpa_dashboard.server:app --reload
```

Visit <http://127.0.0.1:8000> for the overview page. The navigation bar
links to `/operations` and `/revenue`, each returning a manifest tailored for
that view.

## Structure

| File | Purpose |
| ---- | ------- |
| `manifests.py` | Builds the SwarmaKit atom registry, authoring layouts, and manifest payloads (with site metadata and styling hints). |
| `server.py` | Uses the enhanced `mount_layout_app` helper to serve static assets, apply theming, and configure multi-page navigation without hand-written HTML. |
| `README.md` | You are here. |

Feel free to remix the page definitions or extend the manifest helpers to plug
into real data sources.
