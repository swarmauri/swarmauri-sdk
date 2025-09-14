
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_ocr_pytesseract" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_ocr_pytesseract/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_ocr_pytesseract.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_ocr_pytesseract" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/l/swarmauri_ocr_pytesseract" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/v/swarmauri_ocr_pytesseract?label=swarmauri_ocr_pytesseract&color=green" alt="PyPI - swarmauri_ocr_pytesseract"/></a>
</p>

---

# Swarmauri OCR Pytesseract

A model for performing OCR (Optical Character Recognition) using Pytesseract. It can process both local images and image bytes, returning extracted text. Requires Tesseract-OCR to be installed on the system.

## Installation

```bash
pip install swarmauri_ocr_pytesseract
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.ocrs.PytesseractOCR import PytesseractOCR

model = PytesseractOCR()
text = model.extract_text("path/to/image.png")
print(text)
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
