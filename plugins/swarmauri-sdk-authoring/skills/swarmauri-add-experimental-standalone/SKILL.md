---
name: swarmauri-add-experimental-standalone
description: Add an experimental standalone Swarmauri package under pkgs/experimental. Use when Codex needs experimental package scaffolding, planning-stage metadata, optional workspace membership, README branding, entry points when discoverable, registry decisions, tests, and validation.
---

# Swarmauri Add Experimental Standalone

## Workflow

1. Choose `pkgs/experimental/<package_name>` and inspect nearby experimental packages before scaffolding.
2. Create package source, README, `pyproject.toml`, tests, and exports using the closest matching package family.
3. Add metadata: Planning development status, Python 3.10-3.12 classifiers, Apache-2.0, Jacob Stewart as the author, descriptive summary, and experimental keywords.
4. Add workspace membership only when the package should be installed and tested with the workspace; leave it out when the surrounding experimental pattern excludes similar packages.
5. Add entry points only for components intended to be discovered at install time.
6. Add citizenship registry rows only when the resource is meant to appear through the Swarmauri facade; use third-class for generic `swarmauri.plugins` resources.
7. Add scoped tests for behavior, importability, metadata, and entry-point discovery when entry points exist.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/package-readme.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Keep experimental packages under `pkgs/experimental`.
- State explicitly in the final response whether workspace membership and citizenship registry rows were added or intentionally skipped.
- Run validation for the new member when it is in the workspace.
