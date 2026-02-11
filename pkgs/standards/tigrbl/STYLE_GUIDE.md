# Tigrbl Style Guide

## Framework Policy

- Tigrbl code must use **Tigrbl-native interfaces only**.
- Do **not** introduce FastAPI or Starlette dependencies in Tigrbl packages.
- Tigrbl applications are pure **ASGI/WSGI** apps and should rely on Tigrbl's own
  app/router primitives instead of FastAPI/Starlette abstractions.

## Naming Conventions

- **make + CamelCase** — Functions that create and return instances should begin with
  `make` followed by a CamelCase descriptor, e.g. `makeColumn` or `makeVirtualColumn`.
- **define + CamelCase** — Functions that build and return classes should begin with
  `define` and use CamelCase, e.g. `defineApiSpec`.
- **derive + CamelCase** — Functions that produce subclasses from existing classes
  should begin with `derive` in CamelCase form, e.g. `deriveApp`.
