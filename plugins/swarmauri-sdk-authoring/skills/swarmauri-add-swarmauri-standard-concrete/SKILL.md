---
name: swarmauri-add-swarmauri-standard-concrete
description: Add or update a concrete component inside pkgs/swarmauri_standard. Use when Codex needs to implement a first-party standard concrete over an existing base class, update exports, register ComponentBase type metadata, and wire first-class citizenship when discoverable through the swarmauri facade.
---

# Swarmauri Add Swarmauri Standard Concrete

## Workflow

1. Locate the target resource family under `pkgs/swarmauri_standard/swarmauri_standard/<family>/` and inspect sibling concretes.
2. Implement the concrete by inheriting the matching `swarmauri_base` base class.
3. Decorate with `@ComponentBase.register_type(<BaseClass>, "<ConcreteName>")`.
4. Set `type: Literal["<ConcreteName>"] = "<ConcreteName>"`, `version`, and required fields using local conventions.
5. Update family exports and tests.
6. If the component should be visible through `swarmauri.<namespace>.<Name>`, update `PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY`.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Do not add a standalone `pyproject.toml`; this skill is for the existing `swarmauri_standard` package.
- Add or update registry tests when first-class citizenship changes.
- Run validation for `pkgs/swarmauri_standard`; also run `pkgs/swarmauri` tests if citizenship changed.
