![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)


<p align="center">
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_xmp_pdf" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_pdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_xmp_pdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_xmp_pdf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_xmp_pdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_xmp_pdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_xmp_pdf?label=swarmauri_xmp_pdf&color=green" alt="PyPI - swarmauri_xmp_pdf"/></a>
</p>

---

# swarmauri_xmp_pdf

`swarmauri_xmp_pdf` defines the `PDFXMP` scaffold so PDF metadata streams can adopt Swarmauri's XMP lifecycle once implemented.

## Features

- **Future-proof** – defines the API surface for PDF metadata before implementation begins.
- **Registry-integrated** – extends `EmbedXmpBase`, so discovery happens automatically once functionality ships.
- **Clear guidance** – explicit errors communicate the current development status to downstream users.

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

- **Future-proof** – defines the API surface for PDF metadata before implementation begins.
- **Registry-integrated** – extends `EmbedXmpBase`, so discovery happens automatically once functionality ships.
- **Clear guidance** – explicit errors communicate the current development status to downstream users.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk>
- License: Apache 2.0
