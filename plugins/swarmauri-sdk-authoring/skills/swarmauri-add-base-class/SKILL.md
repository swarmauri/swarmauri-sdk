---
name: swarmauri-add-base-class
description: Add or update a Swarmauri SDK base class in pkgs/base/swarmauri_base. Use when Codex needs to implement a base class over a core interface, update ResourceTypes, wire InterfaceRegistry, set ComponentBase registration, exports, and focused tests.
---

# Swarmauri Add Base Class

## Workflow

1. Read the matching core interface and nearby base classes in `pkgs/base/swarmauri_base/<family>/`.
2. Implement the base class by inheriting the core interface and `ComponentBase`; use `@ComponentBase.register_model()` for base models.
3. Set `resource` from `ResourceTypes`, add `type: Literal["<BaseName>"] = "<BaseName>"`, and use existing Pydantic field conventions.
4. Update family exports when the package uses them.
5. If this is a new resource family, update `ResourceTypes` and `pkgs/swarmauri/swarmauri/interface_registry.py`.
6. Add focused tests for importability, resource value, serialization where relevant, and interface-registry lookup when registry wiring changed.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Keep concrete implementations out of `swarmauri_base`.
- Do not add entry points for base classes.
- Run validation for `pkgs/base`; also run `pkgs/swarmauri` tests if `InterfaceRegistry` changed.
