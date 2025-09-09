
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

A parser for reading and extracting data fields from PDF files using PyPDFTK.

## Installation

```bash
pip install swarmauri_parser_pypdftk
```

## Usage
Basic usage example with code snippet:
```python
from swarmauri.parsers.PyPDFTKParser import PyPDFTKParser

parser = PyPDFTKParser()
file_path = "path/to/your/pdf_file.pdf"
documents = parser.parse(file_path)

for document in documents:
    print(document.content)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
