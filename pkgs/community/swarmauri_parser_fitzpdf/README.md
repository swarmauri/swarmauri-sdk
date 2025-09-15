
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_fitzpdf" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_fitzpdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_fitzpdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_fitzpdf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_fitzpdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_fitzpdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_fitzpdf?label=swarmauri_parser_fitzpdf&color=green" alt="PyPI - swarmauri_parser_fitzpdf"/></a>
</p>

---

# Swarmauri Parser Fitz PDF

A parser to extract text from PDF files using PyMuPDF.

## Installation

```bash
pip install swarmauri_parser_fitzpdf
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.FitzPdfParser import PDFtoTextParser

parser = PDFtoTextParser()
file_path = "path/to/your/pdf/file.pdf"
documents = parser.parse(file_path)

for document in documents:
    print(document.content)
    print(document.metadata)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
