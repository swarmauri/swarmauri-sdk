![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_pypdf2/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_pypdf2/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdf2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdf2.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_pypdf2" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdf2/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_pypdf2?label=swarmauri_parser_pypdf2&color=green" alt="PyPI - swarmauri_parser_pypdf2"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser PyPDF2

`swarmauri_parser_pypdf2` is the Swarmauri PDF text parser for page-by-page
extraction using [PyPDF2](https://pypdf2.readthedocs.io/). It converts a PDF
file path or PDF bytes into a list of Swarmauri `Document` objects, preserving
page numbers and source metadata for downstream chunking, indexing, and agent
workflows.

## Why Use Swarmauri Parser PyPDF2

- Extract embedded PDF text without introducing OCR when the document already
  contains readable text objects.
- Preserve page boundaries by returning one `Document` per page.
- Accept either on-disk PDFs or PDF bytes already loaded in memory.
- Keep document ingestion aligned with the Swarmauri parser interface used
  across other loaders and converters.

## FAQ

> **What does this parser return?**  
> A list of Swarmauri `Document` objects, usually one for each page that
> contains extractable text.

> **Can it parse PDF bytes instead of a file path?**  
> Yes. `parse()` accepts either a string path or `bytes`.

> **Does it perform OCR on scanned PDFs?**  
> No. PyPDF2 extracts embedded text. Scanned PDFs without text objects should
> be handled with OCR first.

> **What metadata is attached to each page?**  
> Each returned document includes `page_number` and `source`.

## Features

- Page-by-page PDF text extraction through PyPDF2.
- Supports parsing from local file paths and raw PDF bytes.
- Returns Swarmauri `Document` objects with `content`, `page_number`, and
  `source`.
- Clean fit for ingestion pipelines, retrieval systems, and document analysis
  workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_pypdf2
```

```bash
pip install swarmauri_parser_pypdf2
```

## Usage

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
documents = parser.parse("manuals/device.pdf")

for document in documents:
    print(document.metadata["page_number"])
    print(document.content[:160])
```

## Examples

### Parse a PDF from bytes

```python
from pathlib import Path
from swarmauri_parser_pypdf2 import PyPDF2Parser

pdf_bytes = Path("reports/statement.pdf").read_bytes()
parser = PyPDF2Parser()
pages = parser.parse(pdf_bytes)

for page in pages:
    print(page.metadata)
```

### Send parsed pages to downstream chunking

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
pages = parser.parse("contracts/master-service-agreement.pdf")

for page in pages:
    if page.content.strip():
        print(page.metadata["page_number"], len(page.content))
```

## Related Packages

- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [PyPDF2 text extraction guide](https://pypdf2.readthedocs.io/en/3.x/user/extract-text.html)
- [PyPDF2 documentation](https://pypdf2.readthedocs.io/)
- [PyPDF2 on PyPI](https://pypi.org/project/PyPDF2/)

## Best Practices

- Use this parser when the PDF already contains embedded text.
- Use OCR first for scan-only PDFs, then parse or post-process the OCR output.
- Validate encrypted, malformed, or image-only PDFs earlier in the ingestion
  pipeline so downstream processing can route them correctly.
- Keep in mind that page text extraction quality depends on the PDF's internal
  structure and reading order.

## License

This project is licensed under the Apache-2.0 License.


