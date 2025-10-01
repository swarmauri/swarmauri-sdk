![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_slate" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_slate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_slate.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_slate" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_slate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_slate?label=swarmauri_parser_slate&color=green" alt="PyPI - swarmauri_parser_slate"/></a>
</p>

---

# Swarmauri Parser Slate

PDF text parser for Swarmauri using [Slate3k](https://pypi.org/project/slate3k/) (a lightweight PDFMiner wrapper). Extracts text from each PDF page and returns `Document` instances with page metadata.

## Features

- Opens PDFs with Slate3k and returns a `Document` per page (`content` = text, `metadata` includes `page_number` and `source`).
- Accepts file paths (string). Raises a `TypeError` when given anything else to prevent silent failures.
- Returns an empty list if Slate encounters parsing errors, logging the exception to stdout.

## Prerequisites

- Python 3.10 or newer.
- Slate3k depends on `pdfminer.six`; make sure operating-system libraries required by PDFMiner (e.g., `libxml2`, `libxslt` on Linux) are installed.
- Read access to the PDF path you pass in.

## Installation

```bash
# pip
pip install swarmauri_parser_slate

# poetry
poetry add swarmauri_parser_slate

# uv (pyproject-based projects)
uv add swarmauri_parser_slate
```

## Quickstart

```python
from swarmauri_parser_slate import SlateParser

parser = SlateParser()
documents = parser.parse("pdfs/handbook.pdf")

for doc in documents:
    print(doc.metadata["page_number"], doc.content[:120])
```

## Handling Errors

```python
parser = SlateParser()
try:
    docs = parser.parse("missing.pdf")
    if not docs:
        print("No pages parsed or Slate returned no text.")
except TypeError as exc:
    print(f"Bad input: {exc}")
```

## Tips

- Slate3k works best on text-based PDFs. For scanned/bitmap PDFs, run OCR first (e.g., `swarmauri_ocr_pytesseract`).
- Large PDFs can consume memory; consider chunking results or streaming pages to downstream processors.
- Combine with token counting or summarization measurements in Swarmauri to further process the extracted content.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
