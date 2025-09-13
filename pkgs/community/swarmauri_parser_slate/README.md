<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_parser_pypdftk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_parser_pypdftk)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_parser_pypdftk)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_parser_pypdftk?label=swarmauri_parser_pypdftk&color=green)

</div>

---

# Swarmauri SlateParser

A parser for reading and extracting data fields from PDF files using Slate.

## Installation

```bash
pip install swarmauri_parser_slate
```

## Usage
Basic usage example with code snippet:
```python
from swarmauri.parsers.SlateParser import SlateParser

parser = SlateParser()
file_path = "path/to/your/pdf_file.pdf"
documents = parser.parse(file_path)

for document in documents:
    print(document.content)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
