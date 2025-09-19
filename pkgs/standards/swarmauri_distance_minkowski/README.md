
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_distance_minkowski" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_distance_minkowski.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_distance_minkowski" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/l/swarmauri_distance_minkowski" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_distance_minkowski/">
        <img src="https://img.shields.io/pypi/v/swarmauri_distance_minkowski?label=swarmauri_distance_minkowski&color=green" alt="PyPI - swarmauri_distance_minkowski"/></a>
</p>

---

# Swarmauri Distance Minkowski

A Python package implementing the Minkowski distance metric for vector
comparison within the Swarmauri ecosystem.  The metric generalizes common
distances such as Euclidean (`p = 2`) and Manhattan (`p = 1`).

The distribution issues a `DeprecationWarning` announcing removal in
`v0.10.0`.  Consume the distance through Swarmauri's plugin interfaces or
switch to an alternative implementation before that release.

## Features

- Computes Minkowski distance between vectors using `scipy.spatial.distance`.
- Enforces matching vector dimensionality and raises `ValueError` when shapes
  differ.
- Offers a tunable `p` value along with batch helpers (`distances`,
  `similarities`).
- Derives a similarity score from distance as `1 / (1 + distance)`.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_distance_minkowski
```

```bash
poetry add swarmauri_distance_minkowski
```

```bash
uv pip install swarmauri_distance_minkowski
```

## Usage

```python
from swarmauri_distance_minkowski import MinkowskiDistance
from swarmauri_standard.vectors.Vector import Vector

# Create vectors for comparison
vector_a = Vector(value=[1, 2])
vector_b = Vector(value=[1, 2])

# Initialize Minkowski distance calculator (default p=2 for Euclidean distance)
distance_calculator = MinkowskiDistance()

# Calculate distance between vectors
distance = distance_calculator.distance(vector_a, vector_b)
print(f"Distance: {distance}")

# Calculate similarity between vectors
similarity = distance_calculator.similarity(vector_a, vector_b)
print(f"Similarity: {similarity}")
```

Running the example prints:

```
Distance: 0.0
Similarity: 1.0
```

Customize the `p` value to select different Minkowski norms, or supply a
sequence of vectors to `distances` / `similarities` for batch comparisons.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

