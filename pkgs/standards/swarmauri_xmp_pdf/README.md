![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_xmp_pdf/">
        <img src="https://static.pepy.tech/badge/swarmauri_xmp_pdf/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_pdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_pdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_pdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_pdf?label=swarmauri_xmp_pdf&color=green" alt="PyPI - swarmauri_xmp_pdf"/></a>
</p>

# swarmauri_xmp_pdf

`swarmauri_xmp_pdf` defines the `PDFXMP` scaffold so PDF metadata streams can adopt Swarmauri's XMP lifecycle once implemented.

## Features

- **Future-proof** â€“ defines the API surface for PDF metadata before implementation begins.
- **Registry-integrated** â€“ extends `EmbedXmpBase`, so discovery happens automatically once functionality ships.
- **Clear guidance** â€“ explicit errors communicate the current development status to downstream users.

## Installation

```bash
# pip
pip install swarmauri_xmp_pdf

# uv
uv add swarmauri_xmp_pdf
```

## Usage

```python
from swarmauri_xmp_pdf import PDFXMP

handler = PDFXMP()

try:
    handler.remove_xmp(b"%PDF-1.7...")
except NotImplementedError:
    print("PDF XMP support will arrive in a future release.")
```

### Why it works

- **Future-proof** â€“ defines the API surface for PDF metadata before implementation begins.
- **Registry-integrated** â€“ extends `EmbedXmpBase`, so discovery happens automatically once functionality ships.
- **Clear guidance** â€“ explicit errors communicate the current development status to downstream users.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
