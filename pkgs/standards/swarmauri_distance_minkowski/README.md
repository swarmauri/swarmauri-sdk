
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

A Python package implementing Minkowski distance metric for vector comparison. This distance metric is a generalization that includes both Euclidean and Manhattan distances.

## Installation

```bash
pip install swarmauri_distance_minkowski
```

## Usage

```python
from swarmauri.distances.MinkowskiDistance import MinkowskiDistance
from swarmauri.vectors.Vector import Vector

# Create vectors for comparison
vector_a = Vector(value=[1, 2])
vector_b = Vector(value=[1, 2])

# Initialize Minkowski distance calculator (default p=2 for Euclidean distance)
distance_calculator = MinkowskiDistance()

# Calculate distance between vectors
distance = distance_calculator.distance(vector_a, vector_b)
print(f"Distance: {distance}")  # Output: Distance: 0.0

# Calculate similarity between vectors
similarity = distance_calculator.similarity(vector_a, vector_b)
print(f"Similarity: {similarity}")  # Output: Similarity: 1.0
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

