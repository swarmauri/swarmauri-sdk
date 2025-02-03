![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_parser_fitzpdf)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_parser_fitzpdf)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_parser_fitzpdf)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_parser_fitzpdf?label=swarmauri_parser_fitzpdf&color=green)

</div>

---

# Swarmauri FitzPDF Parser

A parser to extract text from PDF files using PyMuPDF.

## Installation

```bash
pip install swarmauri_parser_fitzpdf
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri_parser_fitzpdf.FitzPdfParser import PDFtoTextParser

parser = PDFtoTextParser()
file_path = "path/to/your/pdf/file.pdf"
documents = parser.parse(file_path)

for document in documents:
    print(document.content)
    print(document.metadata)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
