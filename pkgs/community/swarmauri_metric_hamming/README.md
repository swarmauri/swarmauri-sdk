![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_metric_hamming" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_metric_hamming/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_metric_hamming.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_metric_hamming" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/l/swarmauri_metric_hamming" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_metric_hamming/">
        <img src="https://img.shields.io/pypi/v/swarmauri_metric_hamming?label=swarmauri_metric_hamming&color=green" alt="PyPI - swarmauri_metric_hamming"/></a>
</p>

---

# Swarmauri Metric Hamming

The `swarmauri_metric_hamming` package delivers a production-ready implementation of the Hamming distance that integrates seamlessly with the Swarmauri metric ecosystem. It extends `MetricBase` with binary vector validation, pairwise distance calculations, and axiom verification utilities designed for error-correcting code workflows.

## Features

- ✅ Fully compliant `MetricBase` implementation for binary sequences.
- 🔁 Pairwise and batched distance calculations for matrices, vectors, and iterables.
- 🧪 Built-in validation helpers for metric axioms and input compatibility checks.
- 🧰 Utility conversion helpers for strings, dictionaries, NumPy arrays, and Swarmauri matrices/vectors.

## Installation

### Using `uv`

```bash
uv pip install swarmauri_metric_hamming
```

### Using `pip`

```bash
pip install swarmauri_metric_hamming
```

## Usage

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()

codeword = [1, 0, 1, 1, 0, 0, 1]
received = [1, 1, 1, 1, 0, 0, 1]

# Compute the Hamming distance between two binary vectors
print(metric.distance(codeword, received))  # 1.0

# Verify the metric axioms for the provided inputs
assert metric.check_symmetry(codeword, received)
assert metric.check_triangle_inequality(codeword, received, codeword)
```

## Support

- Python 3.10, 3.11, and 3.12
- Licensed under the Apache-2.0 license

## Contributing

We welcome contributions! Please submit issues and pull requests through the [Swarmauri SDK GitHub repository](https://github.com/swarmauri/swarmauri-sdk).
