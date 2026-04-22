---
name: swarmauri-add-base-mixin
description: Add or update a Swarmauri SDK base mixin in pkgs/base/swarmauri_base. Use when Codex needs reusable mixin behavior tied to existing interfaces or base classes, with correct Pydantic inheritance, exports, and tests without unnecessary registry entries.
---

# Swarmauri Add Base Mixin

## Workflow

1. Inspect sibling mixins in the target `swarmauri_base` family before choosing inheritance.
2. Prefer the local mixin pattern: mixins usually inherit the matching core interface and `BaseModel`, or the narrowest existing base needed by sibling code.
3. Add typed fields and methods without registering the mixin as a `ComponentBase` model unless the surrounding family already does so.
4. Update family exports if sibling mixins are exported.
5. Add focused tests for validation behavior, method behavior, and import compatibility.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Do not update `InterfaceRegistry` unless the mixin creates a new resource kind, which should be rare.
- Do not add package entry points for mixins.
- Run validation for `pkgs/base`.
