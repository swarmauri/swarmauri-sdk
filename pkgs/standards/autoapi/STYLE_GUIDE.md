# AutoAPI Style Guide

## Naming Conventions

- **make + CamelCase** — Functions that create and return instances should begin with
  `make` followed by a CamelCase descriptor, e.g. `makeColumn` or `makeVirtualColumn`.
- **define + CamelCase** — Functions that build and return classes should begin with
  `define` and use CamelCase, e.g. `defineApiSpec`.
- **derive + CamelCase** — Functions that produce subclasses from existing classes
  should begin with `derive` in CamelCase form, e.g. `deriveApp`.
