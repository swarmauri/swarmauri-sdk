---
name: swarmauri-add-core-interface
description: Add or update a Swarmauri SDK core interface in pkgs/core/swarmauri_core. Use when Codex needs to create interface protocols or ABCs, update package exports, add focused tests, or prepare a new resource kind for later base-class and registry wiring.
---

# Swarmauri Add Core Interface

## Workflow

1. Inspect the target family under `pkgs/core/swarmauri_core/<family>/` and read nearby interfaces before editing.
2. Add the interface as an `I<Name>.py` file using existing ABC style: import `ABC` and `abstractmethod`, type the method signatures, and keep bodies as `pass`.
3. Update the family `__init__.py` only if that package already exports sibling interfaces or consumers need the new import path.
4. Add focused tests under `pkgs/core/tests` when behavior can be validated structurally; otherwise add import/signature coverage in the closest existing test location.
5. Record whether the interface introduces a new resource namespace that will need a base class, `ResourceTypes`, and `InterfaceRegistry` wiring in follow-up work.

## Required References

Read these before changing files:

- `../../references/repo-patterns.md`
- `../../references/inheritance-entrypoints.md`
- `../../references/registry-rules.md`

## Completion Checks

- Keep the interface in `swarmauri_core`, not `swarmauri_base`.
- Do not update `PluginCitizenshipRegistry` for interface-only changes.
- Run the package validation commands from `../../references/repo-patterns.md` for `pkgs/core`.
