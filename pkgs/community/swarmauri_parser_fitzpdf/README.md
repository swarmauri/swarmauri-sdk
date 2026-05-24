![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_fitzpdf/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_fitzpdf/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_fitzpdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_fitzpdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_fitzpdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_fitzpdf?label=swarmauri_parser_fitzpdf&color=green" alt="PyPI - swarmauri_parser_fitzpdf"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser Fitz PDF

PDF-to-text parser for Swarmauri built on [PyMuPDF (`pymupdf`)](https://pymupdf.readthedocs.io/). Extracts text from every page of a PDF and returns a `Document` object with the aggregated content and source metadata.

## Features

- Opens PDFs via PyMuPDF and collects text per page.
- Emits a single `Document` with `content` containing the combined text and `metadata['source']` holding the file path.
- Raises a clear error if the input is not a file path string; returns an empty list if PyMuPDF encounters parsing failures.

## Prerequisites

- Python 3.10 or newer.
- PyMuPDF (`pymupdf`) along with system dependencies (X11 libraries on Linux, poppler on some distros). Install OS packages listed in [PyMuPDF docs](https://pymupdf.readthedocs.io/en/latest/installation.html) before pip installing if needed.
- Read access to the PDF files you plan to parse.

## Installation

```bash
# pip
pip install swarmauri_parser_fitzpdf

# poetry
poetry add swarmauri_parser_fitzpdf

# uv (pyproject-based projects)
uv add swarmauri_parser_fitzpdf
```

## Quickstart

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
documents = parser.parse("reports/quarterly.pdf")

for doc in documents:
    print(doc.metadata["source"])
    print(doc.content[:500])
```

## Handling Errors

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
try:
    docs = parser.parse("missing.pdf")
    if not docs:
        print("Parsing failed or returned no content.")
except ValueError as exc:
    print(f"Bad input: {exc}")
```

## Tips

- Pre-process PDFs (deskew, OCR) before parsing if they contain scanned pages without embedded text; PyMuPDF only extracts existing text objects.
- For multi-document pipelines, pair this parser with Swarmauri token-count measurements or summarizers to chunk large PDFs.
- Cache parsed output if the same PDF is accessed frequentlyâ€”parsing large documents repeatedly is expensive.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


