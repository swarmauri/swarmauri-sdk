![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_metric_hamming" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_metric_hamming/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_metric_hamming.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_metric_hamming" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/l/swarmauri_metric_hamming" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/v/swarmauri_metric_hamming?label=swarmauri_metric_hamming&color=green" alt="PyPI - swarmauri_metric_hamming"/></a>
</p>

---

# Swarmauri Hamming Metric

`swarmauri_metric_hamming` packages a reusable implementation of the Hamming
metric for the Swarmauri ecosystem.  The component extends the
`MetricBase` abstraction so it can be composed with other SDK primitives like
matrices, vectors, and error-correcting codes.

## Features

- Drop-in `MetricBase` implementation that validates metric axioms.
- Distance, collection-wise distance and normalised distance helpers.
- Convenience utilities for computing Hamming weight.
- Forms the foundation for error-correcting code utilities such as the
  `(7, 4)` Hamming matrix package.

## Installation

Install the package with your preferred Python tooling:

```bash
pip install swarmauri_metric_hamming
```

```bash
uv pip install swarmauri_metric_hamming
```

## Usage

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
print(metric.distance([1, 0, 1, 1], [1, 1, 0, 1]))      # -> 2.0
print(metric.normalized_distance("abcd", "abcf"))      # -> 0.25
print(metric.weight([0, 0, 1, 0, 1, 1, 0]))             # -> 3.0
```

The metric integrates seamlessly with any Swarmauri component expecting a
`MetricBase` implementation.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
