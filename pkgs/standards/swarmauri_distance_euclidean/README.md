![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

# Swarmauri Distance Euclidean

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.metrics.EuclideanMetric.EuclideanMetric`
- Vector-store replacement: `swarmauri_base.vector_stores.VectorStoreComparator.MetricVectorStoreComparator`

## Compatibility Scope

- Re-exports `EuclideanDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Migration Example

```python
from swarmauri_standard.metrics.EuclideanMetric import EuclideanMetric

metric = EuclideanMetric()
distance = metric.distance([0.0, 0.0], [1.0, 1.0])
```

## Legacy Installation

```bash
uv pip install swarmauri_distance_euclidean
```

```bash
pip install swarmauri_distance_euclidean
```
