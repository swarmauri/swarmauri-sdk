![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_pypdftk" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdftk/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdftk.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_pypdftk" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_pypdftk" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_pypdftk?label=swarmauri_parser_pypdftk&color=green" alt="PyPI - swarmauri_parser_pypdftk"/></a>
</p>

---

# Swarmauri Parser PyPDFTK

Form-field parser for Swarmauri built on [PyPDFTK](https://pypi.org/project/pypdftk/). Extracts PDF AcroForm field metadata and returns it as Swarmauri `Document` content.

## Features

- Calls `pypdftk.dump_data_fields` to extract field key/value pairs.
- Emits a single `Document` with newline-delimited `key: value` text and `metadata['source']` set to the PDF path.
- Returns an empty list when no form fields exist or when parsing fails (logs the error).

## Prerequisites

- Python 3.10 or newer.
- PyPDFTK plus the `pdftk`/`pdftk-java` binary available on the system path. Install operating-system packages: e.g., `apt install pdftk-java` or download `pdftk` for macOS/Windows.
- Read access to the PDF file path you provide.

## Installation

```bash
# pip
pip install swarmauri_parser_pypdftk

# poetry
poetry add swarmauri_parser_pypdftk

# uv (pyproject-based projects)
uv add swarmauri_parser_pypdftk
```

## Quickstart

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
documents = parser.parse("forms/enrollment.pdf")

for doc in documents:
    print(doc.metadata["source"])
    print(doc.content)
```

Example output:
```
source: forms/enrollment.pdf
GivenName: John
FamilyName: Doe
BirthDate: 1990-01-01
```

## Handling Missing Fields

```python
parser = PyPDFTKParser()
docs = parser.parse("forms/plain.pdf")

if not docs:
    print("No form fields detected or parsing failed.")
```

## Tips

- Ensure `pdftk` is installed and available on `PATH`; PyPDFTK delegates to the binary.
- For encrypted PDFs, remove or provide the password before parsing; `pdftk` cannot dump fields from password-protected documents without credentials.
- Combine with other Swarmauri parsers to extract both structured form data (`PyPDFTKParser`) and free-form text (`PyPDF2Parser` or `FitzPdfParser`).

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
