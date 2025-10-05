![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_matrix_hamming74" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_matrix_hamming74/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_matrix_hamming74.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_matrix_hamming74" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/l/swarmauri_matrix_hamming74" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/v/swarmauri_matrix_hamming74?label=swarmauri_matrix_hamming74&color=green" alt="PyPI - swarmauri_matrix_hamming74"/></a>
</p>

---

# Swarmauri Hamming (7, 4) Matrix

`swarmauri_matrix_hamming74` delivers a production-ready generator matrix for
the binary `(7, 4)` Hamming code.  The component extends `MatrixBase` and uses
the companion `swarmauri_metric_hamming` package to reason about codeword
distances and minimum distance properties.

## Features

- Canonical `(7, 4)` generator and parity-check matrices with validation.
- Message encoding, syndrome computation, and single-bit error correction
  helpers.
- Integration with the Swarmauri Hamming metric for distance measurements.
- Utilities to enumerate all codewords and compute the minimum distance of the
  code.

## Installation

Install the package with your preferred Python tooling:

```bash
pip install swarmauri_matrix_hamming74 swarmauri_metric_hamming
```

```bash
uv pip install swarmauri_matrix_hamming74 swarmauri_metric_hamming
```

## Usage

```python
from swarmauri_matrix_hamming74 import Hamming74Matrix

matrix = Hamming74Matrix()
message = [1, 0, 1, 1]
codeword = matrix.encode(message)
print("Codeword:", codeword)

received = codeword.copy()
received[3] ^= 1  # introduce a single-bit error
corrected = matrix.correct(received)
print("Corrected:", corrected)

print("Syndrome:", matrix.syndrome(received))
print("Minimum distance:", matrix.minimum_distance())
```

The matrix exposes convenience helpers for error detection while preserving the
`MatrixBase` contract so it can interoperate with the rest of the Swarmauri
SDK.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
