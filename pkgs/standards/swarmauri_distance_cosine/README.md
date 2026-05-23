![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

# Swarmauri Distance Cosine

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.similarities.CosineSimilarity.CosineSimilarity`
- Vector-store replacement: `swarmauri_standard.vector_stores.CosineSimilarityComparator.CosineSimilarityComparator`

## Compatibility Scope

- Re-exports `CosineDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Migration Example

```python
from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

similarity = CosineSimilarity()
score = similarity.similarity([1.0, 0.0], [1.0, 0.0])
```

## Legacy Installation

```bash
uv pip install swarmauri_distance_cosine
```

```bash
pip install swarmauri_distance_cosine
```
