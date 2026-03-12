![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_distance_wasserstein/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_distance_wasserstein" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_wasserstein/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_wasserstein.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_wasserstein/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_distance_wasserstein" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_wasserstein/">
        <img src="https://img.shields.io/pypi/l/swarmauri_distance_wasserstein" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_wasserstein/">
        <img src="https://img.shields.io/pypi/v/swarmauri_distance_wasserstein?label=swarmauri_distance_wasserstein&color=green" alt="PyPI - swarmauri_distance_wasserstein"/></a>
</p>

---

# Swarmauri Distance Wasserstein

`swarmauri_distance_wasserstein` provides a Swarmauri-compatible distance class
for computing the first Wasserstein distance (Earth Mover's Distance) between
numeric vectors.

## Features

- Implements `WassersteinDistance` as a `DistanceBase` plugin.
- Computes distance using a built-in pure-Python 1D Wasserstein implementation.
- Includes helper methods for batched `distances` and `similarities`.
- Supports Python 3.10, 3.11, and 3.12.

## Installation

```bash
uv pip install swarmauri_distance_wasserstein
```

```bash
pip install swarmauri_distance_wasserstein
```

## Usage

```python
from swarmauri_distance_wasserstein import WassersteinDistance
from swarmauri_standard.vectors.Vector import Vector

vector_a = Vector(value=[0.0, 1.0, 2.0])
vector_b = Vector(value=[0.0, 1.0, 2.0])

distance_calculator = WassersteinDistance()

distance = distance_calculator.distance(vector_a, vector_b)
similarity = distance_calculator.similarity(vector_a, vector_b)

print(f"Distance: {distance}")
print(f"Similarity: {similarity}")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.
