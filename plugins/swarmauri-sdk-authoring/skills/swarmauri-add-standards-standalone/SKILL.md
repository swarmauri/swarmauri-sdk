---
name: swarmauri-add-standards-standalone
description: Add a first-class standalone Swarmauri package under pkgs/standards. Use when Codex needs package scaffolding, workspace membership, pyproject metadata, Swarmauri or Tigrbl branding, entry points, first-class citizenship registry rows, exports, tests, and validation.
---

# Swarmauri Add Standards Standalone

## Workflow

1. Choose `pkgs/standards/<package_name>` and derive the import package from existing naming conventions.
2. Create package source, `pyproject.toml`, README, tests, and exports from the closest standards package example.
3. Add metadata: Planning development status, Python 3.10-3.12 classifiers, Apache-2.0, Jacob Stewart as the author, descriptive summary, and detailed keywords.
4. Add workspace membership in `pkgs/pyproject.toml` unless the user explicitly wants it out of the workspace.
5. Add entry points for discoverable components under the correct `swarmauri.<namespace>` group.
6. Add `PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY` rows for facade-visible resources.
7. Add tests for version metadata, importability, entry-point discovery, behavior, and registry wiring.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/package-readme.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Use Swarmauri branding unless the package is clearly Tigrbl.
- Include both `uv` and `pip` install instructions.
- Run validation for the new member and `pkgs/swarmauri` when citizenship changed.
