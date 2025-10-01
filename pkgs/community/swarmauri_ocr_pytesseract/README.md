![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

OCR adapter for Swarmauri built on top of [PyTesseract](https://pypi.org/project/pytesseract/). Accepts paths, bytes, or PIL images, and exposes synchronous, async, and batch APIs for extracting text.

## Features

- Wraps Tesseract OCR via PyTesseract behind Swarmauri's `OCRBase` interface.
- Supports multiple languages (`language` parameter) and custom Tesseract configs.
- Handles individual, async, and batched OCR calls with optional concurrency limits.
- Helper to list installed Tesseract languages through `get_supported_languages()`.

## Prerequisites

- Python 3.10 or newer.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on the host (`tesseract` binary reachable on `PATH` or via `TESSERACT_CMD`).
- `pytesseract`, `Pillow`, and related dependencies (installed automatically with this package).

## Installation

```bash
# pip
pip install swarmauri_ocr_pytesseract

# poetry
poetry add swarmauri_ocr_pytesseract

# uv (pyproject-based projects)
uv add swarmauri_ocr_pytesseract
```

## Quickstart

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng")
text = ocr.extract_text("docs/invoice.png")
print(text)
```

## Processing Image Bytes

```python
from pathlib import Path
from swarmauri_ocr_pytesseract import PytesseractOCR

png_bytes = Path("receipts/ticket.png").read_bytes()
ocr = PytesseractOCR(language="eng", config="--psm 6")
print(ocr.extract_text(png_bytes))
```

## Async and Batch APIs

```python
import asyncio
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="fra")

async def run_async():
    text = await ocr.aextract_text("scans/document_fr.png")
    print(text)

    texts = await ocr.abatch([
        "scans/page1.png",
        "scans/page2.png",
    ], max_concurrent=2)
    for page, content in enumerate(texts, start=1):
        print(f"Page {page}: {content[:80]}")

# asyncio.run(run_async())
```

## List Available Languages

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR()
print(ocr.get_supported_languages())
```

## Tips

- Set `TESSERACT_CMD` if the binary lives outside standard locations (e.g., Windows installs).
- Use appropriate page segmentation modes (`--psm`) and OCR engine modes (`--oem`) through the `config` parameter to improve quality.
- Pre-process images (grayscale, thresholding) before passing them to the OCR for better accuracy.
- When running in containers, ensure Tesseract language packs (`.traineddata`) are installed for the languages you plan to use.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
