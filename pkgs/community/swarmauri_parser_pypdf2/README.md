![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_pypdf2" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdf2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdf2.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_pypdf2" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_pypdf2" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_pypdf2?label=swarmauri_parser_pypdf2&color=green" alt="PyPI - swarmauri_parser_pypdf2"/></a>
</p>

---

# Swarmauri Parser PyPDF2

Lightweight PDF parser for Swarmauri that uses [PyPDF2](https://pypdf2.readthedocs.io/) to extract text from each page. Returns a `Document` per page with metadata describing the source file and page number.

## Features

- Handles PDF input from file paths or raw bytes.
- Produces one `Document` per page, storing text in `content` and metadata fields (`page_number`, `source`).
- Gracefully returns an empty list if PyPDF2 cannot extract text from a page (e.g., scanned PDFs without OCR).

## Prerequisites

- Python 3.10 or newer.
- PyPDF2 (installed automatically). For encrypted PDFs, ensure you provide access credentials before parsing.

## Installation

```bash
# pip
pip install swarmauri_parser_pypdf2

# poetry
poetry add swarmauri_parser_pypdf2

# uv (pyproject-based projects)
uv add swarmauri_parser_pypdf2
```

## Quickstart

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
documents = parser.parse("manuals/device.pdf")

for doc in documents:
    print(doc.metadata["page_number"], doc.content[:120])
```

## Parsing PDF Bytes

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

with open("statements/bank.pdf", "rb") as f:
    pdf_bytes = f.read()

parser = PyPDF2Parser()
pages = parser.parse(pdf_bytes)
print(len(pages), "pages parsed from bytes")
```

## Tips

- PyPDF2 extracts text only when the PDF contains accessible text objects. For scanned documents, run OCR first (e.g., with `swarmauri_ocr_pytesseract`).
- Remove or handle password protection before parsing; PyPDF2 cannot decrypt files without the password.
- Combine this parser with Swarmauri chunkers or summarizers to process large documents efficiently.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
