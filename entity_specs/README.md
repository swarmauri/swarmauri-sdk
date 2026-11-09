# Swarmauri Entity Specs

This directory holds the bootstrap inventory and source specs for generated
Swarmauri entities. The manifest is generated from the current Python source so
the first cut can inventory the existing surface without importing package code.
The files under `sources/` are the editable pilot source specs that future
generators should treat as the durable authority.

Run these commands from the repository root:

```bash
python scripts/generate_entity_manifest.py generate
python scripts/generate_entity_manifest.py check
python scripts/generate_entity_manifest.py validate
python scripts/generate_entities.py check
```

The manifest scope includes:

- `swarmauri_core`
- `swarmauri_base`
- `swarmauri_standard`
- workspace packages named `swarmauri_*`
- legacy typo packages named `swamauri_*` when they expose Swarmauri entities

The manifest scope excludes `peagen`, all `tigr*` packages, `tigrcorn`, example
packages, tests, caches, build outputs, and virtual environments.

Future language generators should consume `swarmauri_entities.v1.json` and emit
Python, Rust, npm TypeScript, TSX, React TSX, Vue TSX, and Svelte TSX outputs
from that manifest while source specs are bootstrapped. Once a family has a
source spec, generators should prefer the source spec over rediscovering Python
classes independently.

## Source Specs

`sources/documents.v1.json` is the first pilot source spec. It describes
`DocumentBase` and `Document` with stable entity ids, generator targets,
registration metadata, and fields. The `validate` command checks source specs
against the bootstrap manifest so stale ids, roles, or missing required fields
fail before generators consume them. `scripts/generate_entities.py check`
renders the documents Python files in memory and compares them against the
current package sources without rewriting package files.
