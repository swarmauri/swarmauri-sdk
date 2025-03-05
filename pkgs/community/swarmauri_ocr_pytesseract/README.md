
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_ocr_pytesseract" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_ocr_pytesseract/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_ocr_pytesseract/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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
