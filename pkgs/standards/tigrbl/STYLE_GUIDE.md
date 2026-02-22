# Tigrbl Style Guide

## Naming Conventions

- **make + CamelCase** — Functions that create and return instances should begin with
  `make` followed by a CamelCase descriptor, e.g. `makeColumn` or `makeVirtualColumn`.
- **define + CamelCase** — Functions that build and return classes should begin with
  `define` and use CamelCase, e.g. `defineApiSpec`.
- **derive + CamelCase** — Functions that produce subclasses from existing classes
  should begin with `derive` in CamelCase form, e.g. `deriveApp`.

## Framework Policy

- Tigrbl packages must use **Tigrbl-native APIs only** for application and router construction.
- Do **not** introduce ASGI- or Starlette-specific application objects, routers, lifecycle hooks, request/response abstractions, or middleware as core framework dependencies.
- Treat Tigrbl as a pure ASGI/WSGI framework surface: build services with `TigrblApp`, `TigrblRouter`, and related Tigrbl primitives.
- **No ASGI, no Starlette.** Do not introduce runtime or test dependencies on either framework.

