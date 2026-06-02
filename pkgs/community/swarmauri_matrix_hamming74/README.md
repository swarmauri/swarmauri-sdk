![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_matrix_hamming74/">
        <img src="https://static.pepy.tech/badge/swarmauri_matrix_hamming74/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_matrix_hamming74/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_matrix_hamming74.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/l/swarmauri_matrix_hamming74" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_matrix_hamming74/">
        <img src="https://img.shields.io/pypi/v/swarmauri_matrix_hamming74?label=swarmauri_matrix_hamming74&color=green" alt="PyPI - swarmauri_matrix_hamming74"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Matrix Hamming(7,4)

The `swarmauri_matrix_hamming74` package provides a binary Hamming (7,4) code matrix that extends `MatrixBase`. It includes generator and parity-check representations, encoding and decoding helpers, and tight integration with the `swarmauri_metric_hamming` package for error detection and correction workflows.

## Features

- Binary matrix implementation built on `MatrixBase` with full indexing and arithmetic support.
- Generator and parity-check matrix accessors for classic Hamming (7,4) coding schemes.
- Encoding, syndrome calculation, and nearest-codeword decoding helpers powered by the Hamming metric.
- Binary-safe matrix operations (addition, subtraction, multiplication, and matrix multiplication modulo 2).

## Installation

### Using `uv`

```bash
uv pip install swarmauri_matrix_hamming74
```

### Using `pip`

```bash
pip install swarmauri_matrix_hamming74
```

## Usage

```python
from swarmauri_matrix_hamming74 import Hamming74Matrix

matrix = Hamming74Matrix()
message = [1, 0, 1, 1]
codeword = matrix.encode(message)

# Introduce a single-bit error
received = codeword.copy()
received[3] ^= 1

# Decode using syndrome lookup and Hamming distance search
nearest = matrix.nearest_codeword(received)
print(nearest)  # Recovers the original codeword
```

## Support

- Python 3.10, 3.11, and 3.12
- Licensed under the Apache-2.0 license

## Contributing

We welcome contributions! Please submit issues and pull requests through the [Swarmauri SDK GitHub repository](https://github.com/swarmauri/swarmauri-sdk).


