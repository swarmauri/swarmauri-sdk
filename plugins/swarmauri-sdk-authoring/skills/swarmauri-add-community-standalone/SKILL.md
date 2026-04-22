---
name: swarmauri-add-community-standalone
description: Add a second-class standalone Swarmauri package under pkgs/community. Use when Codex needs community package scaffolding, workspace membership, pyproject metadata, README branding, entry points, second-class citizenship rows, exports, tests, and validation.
---

# Swarmauri Add Community Standalone

## Workflow

1. Choose `pkgs/community/<package_name>` and inspect the closest community package with the same resource family.
2. Create package source, README, `pyproject.toml`, tests, and exports.
3. Add metadata: Planning development status, Python 3.10-3.12 classifiers, Apache-2.0, Jacob Stewart as the author, descriptive summary, and package-specific keywords.
4. Add workspace membership in `pkgs/pyproject.toml` unless explicitly excluded.
5. Add entry points under the correct `swarmauri.<namespace>` group for discoverable resources.
6. Add `PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY` rows for facade-visible resources.
7. Add tests for behavior, version metadata, importability, entry-point discovery, and registry wiring.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/package-readme.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Do not place community packages under `pkgs/standards`.
- Use second-class registry rows, not first-class rows.
- Run validation for the new member and `pkgs/swarmauri` when citizenship changed.
