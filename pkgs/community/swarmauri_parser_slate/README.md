<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
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
