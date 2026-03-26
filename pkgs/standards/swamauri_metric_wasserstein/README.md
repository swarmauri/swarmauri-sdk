![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/dm/swamauri_metric_wasserstein" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swamauri_metric_wasserstein.svg"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/pyversions/swamauri_metric_wasserstein" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/l/swamauri_metric_wasserstein" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swamauri_metric_wasserstein/">
        <img src="https://img.shields.io/pypi/v/swamauri_metric_wasserstein?label=swamauri_metric_wasserstein&color=green" alt="PyPI - swamauri_metric_wasserstein"/></a>
</p>

---

# Swamauri Metric Wasserstein

`swamauri_metric_wasserstein` provides a Swarmauri-compatible metric class
for computing the first Wasserstein distance (Earth Mover's Distance) between
numeric vectors.

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
