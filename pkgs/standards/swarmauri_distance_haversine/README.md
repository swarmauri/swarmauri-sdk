![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

# Swarmauri Distance Haversine

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Current state: no active drop-in Haversine metric package exists in the workspace.
- Migration path: use an active metric or similarity from `swarmauri_standard`, or adapt a geospatial implementation through `swarmauri_base.vector_stores.VectorStoreComparator`.

## Compatibility Scope

- Re-exports `HaversineDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Legacy Installation

```bash
uv pip install swarmauri_distance_haversine
```

```bash
pip install swarmauri_distance_haversine
```
