
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

A parser for reading and extracting text from PDF files using PyPDF2.

## Installation

```bash
pip install swarmauri_parser_pypdf2
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.PyPDF2Parser import PyPDF2Parser

parser = PyPDF2Parser()

# Parsing from a file path
documents = parser.parse("path/to/your/file.pdf")
for doc in documents:
    print(doc.content)

# Parsing from bytes
pdf_bytes = b"%PDF-1.4 ... (binary content)"
documents = parser.parse(pdf_bytes)
for doc in documents:
    print(doc.content)
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
