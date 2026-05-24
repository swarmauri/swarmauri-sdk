![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_metric_hamming/">
        <img src="https://static.pepy.tech/badge/swarmauri_metric_hamming/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_metric_hamming/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_metric_hamming.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/l/swarmauri_metric_hamming" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/v/swarmauri_metric_hamming?label=swarmauri_metric_hamming&color=green" alt="PyPI - swarmauri_metric_hamming"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Metric Hamming

`swarmauri_metric_hamming` is the Swarmauri metric implementation for Hamming
distance. It compares equal-length sequences and returns the count of positions
that differ, while also exposing batched distance helpers and metric-axiom
checks for downstream validation workflows.

## Why Use Swarmauri Metric Hamming

- Measure discrete sequence differences inside Swarmauri retrieval, coding,
  validation, or comparison workflows.
- Compare binary vectors, strings, NumPy arrays, and Swarmauri vector or matrix
  surfaces through one metric component.
- Reuse a metric implementation that also exposes symmetry, identity, and
  triangle-inequality checks.
- Build exact distance-based workflows for error-correcting codes, bitstring
  analysis, and symbolic comparison.

## FAQ

> **What does `distance()` return?**  
> A float equal to the number of differing positions between two equal-length
> inputs.

> **What input types are supported?**  
> Strings, bytes, dictionaries, NumPy arrays, generic sequences, and
> Swarmauri matrix/vector interfaces.

> **Does it normalize the distance?**  
> No. The current implementation returns the raw count of mismatched positions.

> **Can it compare batches of vectors?**  
> Yes. Use `distances()` to generate pairwise distance rows across collections.

## Features

- Raw Hamming distance for equal-length sequences.
- Pairwise `distances()` support for collections of vectors.
- Input normalization for strings, bytes, dicts, arrays, matrices, and
  vectors.
- Metric-axiom helpers: non-negativity, symmetry, identity of indiscernibles,
  and triangle inequality.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_metric_hamming
```

```bash
pip install swarmauri_metric_hamming
```

## Usage

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
codeword = [1, 0, 1, 1, 0, 0, 1]
received = [1, 1, 1, 1, 0, 0, 1]

print(metric.distance(codeword, received))
```

## Examples

### Compare binary vectors

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
print(metric.distance([1, 0, 1, 1], [1, 1, 0, 1]))
```

### Compare strings and arrays

```python
import numpy as np
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
left = "1011001"
right = np.array([1, 0, 1, 0, 0, 0, 1])

print(metric.distance(left, right))
```

### Compute pairwise distances across collections

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
left = [[0, 0, 0], [1, 1, 1]]
right = [[0, 0, 1], [1, 0, 1]]

print(metric.distances(left, right))
```

### Verify metric axioms

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
x = [0, 1, 0, 1]
y = [0, 0, 1, 1]
z = [1, 0, 1, 0]

assert metric.check_non_negativity(x, y)
assert metric.check_symmetry(x, y)
assert metric.check_triangle_inequality(x, y, z)
```

## Related Packages

- [swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)
- [swarmauri_measurement_tokencountestimator](https://pypi.org/project/swarmauri_measurement_tokencountestimator/)
- [swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

## More Documentation

- [Hamming distance overview](https://en.wikipedia.org/wiki/Hamming_distance)
- [NumPy documentation](https://numpy.org/doc/)

## Best Practices

- Validate equal-length inputs before calling `distance()` in external
  pipelines.
- Use raw Hamming counts when exact mismatch positions matter more than a
  normalized ratio.
- Normalize heterogeneous input types consistently before comparing large
  collections.
- Pair this metric with domain-specific encoders when comparing symbolic or
  categorical data.

## License

This project is licensed under the Apache-2.0 License.

