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

`swarmauri_parser_fitzpdf` is the Swarmauri PDF parser for high-performance
text extraction using [PyMuPDF](https://pymupdf.readthedocs.io/). It opens a
PDF, extracts text from every page, and returns a single Swarmauri `Document`
with the aggregated content and source metadata.

## Why Use Swarmauri Parser Fitz PDF

- Use PyMuPDF's fast document engine for PDF extraction inside Swarmauri
  ingestion and indexing pipelines.
- Produce one normalized `Document` for whole-file workflows such as
  summarization, classification, or chunking after parse.
- Keep PDF parsing logic aligned with the Swarmauri parser interface used by
  other loaders and processors.
- Stay flexible if you later need PyMuPDF-specific extraction modes or OCR
  augmentation upstream.

## FAQ

> **What does this parser return?**  
> A list containing one Swarmauri `Document` whose `content` holds the combined
> extracted text for the PDF.

> **Does it return one document per page?**  
> No. This parser aggregates all page text into a single document.

> **Can it parse scanned PDFs with no text layer?**  
> Not by itself. PyMuPDF extracts text objects already present in the document.
> Scan-only PDFs should be OCR'd first.

> **What input type does it expect?**  
> A file path string pointing to a local PDF.

## Features

- Aggregated PDF text extraction through PyMuPDF.
- Preserves the original source path in document metadata.
- Uses a lightweight Swarmauri parser surface for document pipelines.
- Appropriate for whole-document ingestion, chunking, and retrieval setup.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_fitzpdf
```

```bash
pip install swarmauri_parser_fitzpdf
```

## Usage

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
documents = parser.parse("reports/quarterly.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content[:500])
```

## Examples

### Parse a PDF into a single document

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
docs = parser.parse("whitepapers/roadmap.pdf")

if docs:
    print(len(docs[0].content))
```

### Handle invalid input safely

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()

try:
    docs = parser.parse("missing.pdf")
    if not docs:
        print("Parsing failed or returned no text.")
except ValueError as exc:
    print(exc)
```

## Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [PyMuPDF basics](https://pymupdf.readthedocs.io/en/latest/the-basics.html)
- [PyMuPDF text extraction details](https://pymupdf.readthedocs.io/en/latest/app1.html)
- [PyMuPDF text recipes](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)

## Best Practices

- Use this parser when you want a whole-document text payload rather than
  page-by-page output.
- Use OCR earlier in the flow for scan-only documents that have no extractable
  text layer.
- Cache parse output for large PDFs if the same files are processed repeatedly.
- If reading order matters, verify the extracted output on representative
  documents because PDF text order depends on document structure.

## License

This project is licensed under the Apache-2.0 License.

