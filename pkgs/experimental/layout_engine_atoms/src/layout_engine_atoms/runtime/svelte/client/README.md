# layout-engine-atoms · Svelte runtime client

This package publishes the browser bundle for the Svelte integration. It mirrors
the Vue runtime's build behaviour so downstream tooling can consume either
framework with consistent expectations.

## Available scripts

- `npm run dev` – Launch Vite with the Svelte plugin for local development.
- `npm run build` – Emit library bundles under `dist/`:
  - `layout-engine-svelte.es.js`
  - `layout-engine-svelte.umd.js`
- `npm run preview` – Preview the production build using Vite's preview server.
- `npm test` – Placeholder script until runtime tests are added.

The Vite configuration (`vite.config.js`) resolves shared helpers from
`runtime/core/` and keeps the output structure aligned with the Vue package so
that publishing workflows remain uniform.
