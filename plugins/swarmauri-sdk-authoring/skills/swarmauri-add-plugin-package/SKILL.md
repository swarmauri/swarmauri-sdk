---
name: swarmauri-add-plugin-package
description: Add a Swarmauri plugin package under pkgs/plugins. Use when Codex needs plugin package scaffolding, swarmauri.plugins or explicit resource entry points, third-class citizenship when appropriate, README branding, pyproject metadata, tests, and validation.
---

# Swarmauri Add Plugin Package

## Workflow

1. Choose `pkgs/plugins/<package_name>` and inspect the closest plugin package before scaffolding.
2. Create package source, README, `pyproject.toml`, tests, and exports.
3. Add metadata: Planning development status, Python 3.10-3.12 classifiers, Apache-2.0, Jacob Stewart as the author, descriptive summary, and plugin-focused keywords.
4. Add workspace membership in `pkgs/pyproject.toml` unless explicitly excluded.
5. Add `[project.entry-points."swarmauri.plugins"]` for generic plugins, or a specific `swarmauri.<namespace>` group when the plugin is also a discoverable resource.
6. Add `PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY` rows for generic `swarmauri.plugins` resources; use first or second class only when the user explicitly asks for facade-visible standard or community citizenship.
7. Add tests for version metadata, entry-point discovery, importability, and plugin behavior.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/package-readme.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Keep Codex plugins under top-level `plugins/`; keep Python plugin packages under `pkgs/plugins/`.
- Include both `uv` and `pip` install instructions.
- Run validation for the new member and `pkgs/swarmauri` when citizenship changed.
