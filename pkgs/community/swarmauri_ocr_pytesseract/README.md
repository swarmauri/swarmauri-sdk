
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
