![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)
<p align="center">
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>
# Swarmauri Distance Levenshtein

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Install it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.metrics.LevenshteinMetric.LevenshteinMetric`

## Compatibility Scope

- Re-exports `LevenshteinDistance` from `swarmauri_standard.distances`.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Migration Example

```python
from swarmauri_standard.metrics.LevenshteinMetric import LevenshteinMetric

metric = LevenshteinMetric()
distance = metric.distance("kitten", "sitting")
```

## Legacy Installation

```bash
uv pip install swarmauri_distance_levenshtein
```

```bash
pip install swarmauri_distance_levenshtein
```



