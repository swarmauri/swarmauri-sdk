![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

# Swarmauri Distance Chi Squared

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Current state: no active drop-in chi-squared metric package exists in the workspace.
- Migration path: use an active similarity from `swarmauri_standard`, or adapt a project-specific implementation through `swarmauri_base.vector_stores.VectorStoreComparator`.

## Compatibility Scope

- Re-exports `ChiSquaredDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Legacy Installation

```bash
uv pip install swarmauri_distance_chi_squared
```

```bash
pip install swarmauri_distance_chi_squared
```
