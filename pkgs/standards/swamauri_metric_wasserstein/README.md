![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

This package is deprecated and will be removed from the active Swarmauri workspace by `0.12.0`.
Use it only as a compatibility shim while migrating away from the deprecated `Distance` contract.

<p align="center">
    <a href="https://pepy.tech/project/swamauri_metric_wasserstein/">
        <img src="https://static.pepy.tech/badge/swamauri_metric_wasserstein/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein.svg"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/l/swamauri_metric_wasserstein" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/v/swamauri_metric_wasserstein?label=swamauri_metric_wasserstein&color=green" alt="PyPI - swamauri_metric_wasserstein"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swamauri Metric Wasserstein

`swamauri_metric_wasserstein` provides a Swarmauri-compatible metric class
for computing the first Wasserstein distance (Earth Mover's Distance) between
numeric vectors.

## Preferred Replacement

- Preferred package: [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- Current state: no active standalone Wasserstein replacement package exists in the workspace.
- Migration path: keep this deprecated package only for compatibility, or vendor a project-specific metric until a correctly named active package is published.

## Features

- Implements `WassersteinMetric` as a `MetricBase` plugin.
- Computes distance using a built-in pure-Python 1D Wasserstein implementation.
- Includes helper methods for batched `distances` and `similarities`.
- Supports Python 3.10, 3.11, and 3.12.

## Installation

```bash
uv pip install swamauri_metric_wasserstein
```

```bash
pip install swamauri_metric_wasserstein
```

## Usage

```python
from swamauri_metric_wasserstein import WassersteinMetric
from swarmauri_standard.vectors.Vector import Vector

vector_a = Vector(value=[0.0, 1.0, 2.0])
vector_b = Vector(value=[0.0, 1.0, 2.0])

distance_calculator = WassersteinMetric()

distance = distance_calculator.distance(vector_a, vector_b)
similarity = distance_calculator.similarity(vector_a, vector_b)

print(f"Distance: {distance}")
print(f"Similarity: {similarity}")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.


