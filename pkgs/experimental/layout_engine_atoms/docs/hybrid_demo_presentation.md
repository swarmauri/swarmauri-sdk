# Hybrid Demo Presentation Outline

## Slide 1 · Vue Thin Wrapper Demo (2–3 min)
- Objective: showcase dual SPA/MPA manifest rendering with realtime WebSocket updates.
- Deliverables now in place:
  - Shared Swiss-grid theme + token defaults.
  - `create_layout_app` helper (production-ready) with manifest/events bootstrap.
  - Hybrid demo runtime (`examples/hybrid_demo`) streaming incidents into SPA + MPA views.
  - Build helpers + documented embedding flow (`docs/` + package README).
- Repo checkpoints:
  - `pkgs/experimental/layout_engine_atoms` (README + docs refresh).
  - `examples/hybrid_demo` application and incident stream coroutine.
  - Reference PRs: Swiss grid theme, Vue runtime docs, Hybrid demo stream, build helper.

## Slide 2 · Architecture / Flow Diagram
- Recommended boxes & arrows for illustrator/diagram tool:
  1. **Python Manifest Builder** → `create_layout_app()`
  2. **ManifestApp (ASGI)** → serves `manifest.json`, `layout-engine-vue.es.js`, handles `/events` WebSocket
  3. **Browser** loads Vue bundle → `createLayoutApp()` bootstrap
  4. **Vue runtime core** pulls helpers (state, theme, events) → renders atom components
  5. **WebSocket channel** loops back into `ManifestEventsConfig` (publish/subscribe bus)
- Notes below diagram:
  - Supports SPA & MPA manifests concurrently.
  - Manifest patches drive UI deltas.
  - Swiss grid token baseline governs spacing, typography, colors.

## Slide 3 · Runtime Data Flow
- **Manifest load**: browser fetches `manifest.json` → `createRuntimeState` hydrates → `DashboardApp` renders.
- **Multi-page support**: `setPage(initialPageId)` selects view; per-page tiles and theme patches merge into runtime view.
- **Theme pipeline**: Swiss grid defaults → manifest/page theme patch → `createDocumentThemeApplier` writes CSS variables.
- **Realtime loop**: `/hybrid-demo/(spa|mpa)/events` WebSocket → manifest patches (incident table rows) → `runtime.applyPatch` → UI refresh + `events.state` update.

## Slide 4 · Live Demo Script (~2 min)
1. **Start backend**
   ```bash
   uv run --directory pkgs/experimental/layout_engine_atoms \
     --package layout-engine-atoms \
     uvicorn examples.hybrid_demo.server:app --reload
   ```
2. **Browser walkthrough**
   - Visit `http://127.0.0.1:8000/hybrid-demo/` landing page.
   - Open SPA dashboard (`/hybrid-demo/spa/`) then MPA dashboard (`/hybrid-demo/mpa/`); highlight navigation between pages.
   - Call out Swiss theme tokens driving body background, tile spacing, accent palette.
3. **Realtime proof**
   - DevTools → Network → WS; inspect `/events` stream for SPA + MPA.
   - Show incident table updates every ~15 s (“Activation Cohort n”, rotating statuses/owners).
   - Optionally run `window.LayoutEngineVue.controller.events.state` (per tab) to display live connection state.
4. **Wrap**
   - Mention Vue bundle published under `layout_engine_atoms/runtime/vue/client/dist/`.
   - Point to embedding docs (`docs/vue_embedding_guide.md`) and Swiss grid tokens (`docs/swiss_grid_theme.md`).

## Slide 5 · Next Steps & PR Pointers
- **PRs ready / in-flight**: Swiss grid theme; Vue runtime docs + README; Hybrid demo incidents stream; build helper wiring.
- **Post-demo focus**:
  - Close React/Svelte parity gap (shared event bridge + theme tokens).
  - Polish production bundle alias / CDN guidance.
  - Optional CLI entry to rebuild Vue assets on demand.
  - Additional demo UX polish (filters, latency indicators).
- **Follow-up questions**:
  - Release cadence for Vue bundle updates.
  - Shared WebSocket topic taxonomy across manifests.
  - Design refinements for Swiss token set + dashboards.

