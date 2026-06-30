![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Use it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_distance_minkowski/">
        <img src="https://static.pepy.tech/badge/swarmauri_distance_minkowski/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/l/swarmauri_distance_minkowski" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/v/swarmauri_distance_minkowski?label=swarmauri_distance_minkowski&color=green" alt="PyPI - swarmauri_distance_minkowski"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Distance Minkowski

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Preferred import: `swarmauri_standard.metrics.LpMetric.LpMetric`
- Migration note: use `LpMetric(p=<order>)` for Minkowski semantics.

## Compatibility Scope

- Re-exports the deprecated `MinkowskiDistance` compatibility shim.
- Emits a `DeprecationWarning` on import.
- Remains compatible only with Swarmauri packages earlier than `0.10.0`.

## Migration Example

```python
from swarmauri_standard.metrics.LpMetric import LpMetric

metric = LpMetric(p=2)
distance = metric.distance([1.0, 2.0], [1.0, 2.0])
similarity = 1.0 if distance == 0.0 else 1.0 / (1.0 + distance)
```

## Legacy Installation

```bash
pip install swarmauri_distance_minkowski
```

```bash
uv pip install swarmauri_distance_minkowski
```


