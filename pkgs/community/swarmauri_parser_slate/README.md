![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_slate/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_slate/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_slate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_slate.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_slate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_slate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_slate?label=swarmauri_parser_slate&color=green" alt="PyPI - swarmauri_parser_slate"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser Slate

`swarmauri_parser_slate` is the Swarmauri PDF parser for page-by-page text
extraction using [slate3k](https://pypi.org/project/slate3k/), a lightweight
wrapper around PDFMiner. It reads a local PDF path, extracts text for each
page, and returns Swarmauri `Document` objects with source and page metadata.

## Why Use Swarmauri Parser Slate

- Parse text-based PDFs into page-scoped `Document` objects for chunking,
  retrieval, and downstream agent workflows.
- Keep document ingestion aligned with the Swarmauri parser interface.
- Use a small PDF extraction dependency when `slate3k` is sufficient for the
  target document set.
- Preserve page numbers so later indexing, annotation, or citation workflows
  can map text back to the source file.

## FAQ

> **What input does this parser accept?**  
> A local PDF file path as a string.

> **Does it support raw PDF bytes?**  
> No. The current implementation is path-only and raises `TypeError` for other
> input types.

> **What does it return?**  
> A list of Swarmauri `Document` objects, usually one per extracted page.

> **Does it perform OCR on scanned PDFs?**  
> No. It is intended for PDFs that already contain extractable text.

## Features

- Page-by-page PDF text extraction through `slate3k`.
- Returns `Document` objects with `page_number` and `source` metadata.
- Provides a clear `TypeError` for unsupported input types.
- Fits Swarmauri ingestion, parsing, and retrieval pipelines.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_slate
```

```bash
pip install swarmauri_parser_slate
```

## Usage

```python
from swarmauri_parser_slate import SlateParser

parser = SlateParser()
documents = parser.parse("pdfs/handbook.pdf")

for document in documents:
    print(document.metadata["page_number"], document.content[:120])
```

## Examples

### Parse a handbook PDF

```python
from swarmauri_parser_slate import SlateParser

parser = SlateParser()
pages = parser.parse("manuals/employee-handbook.pdf")

for page in pages:
    print(page.metadata["page_number"], len(page.content))
```

### Handle missing files and invalid inputs

```python
from swarmauri_parser_slate import SlateParser

parser = SlateParser()

print(parser.parse("missing.pdf"))

try:
    parser.parse(b"%PDF-1.7 ...")
except TypeError as exc:
    print(exc)
```

## Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [slate3k on PyPI](https://pypi.org/project/slate3k/)
- [pdfminer.six documentation](https://pdfminersix.readthedocs.io/)

## Best Practices

- Use this parser for PDFs that already contain selectable text.
- Route scan-only or image-based PDFs through OCR before parsing.
- Keep page-granular output when later stages need per-page provenance.
- Validate representative PDFs first because extraction quality depends on the
  original PDF structure.

## License

This project is licensed under the Apache-2.0 License.


