![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_ocr_pytesseractimg2text)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_ocr_pytesseractimg2text)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_ocr_pytesseractimg2text)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_ocr_pytesseractimg2text?label=swarmauri_ocr_pytesseractimg2text&color=green)

</div>

---

# Swarmauri OCR PytesseractImg2Text

A model for performing OCR (Optical Character Recognition) using Pytesseract. It can process both local images and image bytes, returning extracted text. Requires Tesseract-OCR to be installed on the system.

## Installation

```bash
pip install swarmauri_ocr_pytesseractimg2text
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.ocrs.PytesseractImg2OCR import PytesseractImg2OCR

model = PytesseractImg2OCR()
text = model.extract_text("path/to/image.png")
print(text)
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
