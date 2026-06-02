![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_ocr_pytesseract/">
        <img src="https://static.pepy.tech/badge/swarmauri_ocr_pytesseract/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_ocr_pytesseract/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_ocr_pytesseract.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/l/swarmauri_ocr_pytesseract" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_ocr_pytesseract/">
        <img src="https://img.shields.io/pypi/v/swarmauri_ocr_pytesseract?label=swarmauri_ocr_pytesseract&color=green" alt="PyPI - swarmauri_ocr_pytesseract"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri OCR Pytesseract

`swarmauri_ocr_pytesseract` is the Swarmauri OCR adapter for running local
Tesseract-powered image-to-text extraction through a consistent Swarmauri
`OCRBase` interface. It accepts file paths, raw bytes, or in-memory PIL images
and supports synchronous, asynchronous, and batch OCR workflows.

## Why Use Swarmauri OCR Pytesseract

- Use the same OCR component shape across local and pipeline-based Swarmauri
  workflows.
- Run OCR on local infrastructure without routing images through a hosted API.
- Tune Tesseract language selection and engine flags for receipts, forms,
  scanned PDFs, screenshots, and other document images.
- Reuse the same component in parsing, ingestion, indexing, and agent
  workflows.

## FAQ

> **What does this package do?**  
> It wraps PyTesseract and the local Tesseract binary behind Swarmauri's OCR
> component interface.

> **Does it require a hosted API key?**  
> No. It runs locally, but the host must have the `tesseract` executable and
> any required language packs installed.

> **What image inputs are supported?**  
> File path strings, raw image bytes, and `PIL.Image.Image` instances.

> **Can it process multiple images concurrently?**  
> Yes. Use `batch()` for synchronous lists and `abatch()` for async execution
> with a concurrency limit.

## Features

- Local OCR backed by [PyTesseract](https://pypi.org/project/pytesseract/) and
  [Tesseract OCR](https://tesseract-ocr.github.io/).
- Supports configurable `language`, `config`, and explicit `tesseract_cmd`
  resolution.
- Accepts paths, bytes, and PIL image objects.
- Includes `extract_text`, `aextract_text`, `batch`, and `abatch` methods.
- Can report installed OCR languages through `get_supported_languages()`.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_ocr_pytesseract
```

```bash
pip install swarmauri_ocr_pytesseract
```

System requirement:

- Install the native `tesseract` binary and ensure it is available on `PATH`,
  or set `TESSERACT_CMD` to the executable location.

## Usage

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng", config="--psm 6")
text = ocr.extract_text("docs/invoice.png")
print(text)
```

## Examples

### OCR from image bytes

```python
from pathlib import Path
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng")
image_bytes = Path("receipts/ticket.png").read_bytes()
text = ocr.extract_text(image_bytes)
print(text)
```

### OCR from a PIL image

```python
from PIL import Image
from swarmauri_ocr_pytesseract import PytesseractOCR

image = Image.open("scans/form.png")
ocr = PytesseractOCR(language="eng", config="--oem 3 --psm 4")
print(ocr.extract_text(image))
```

### Async batch OCR

```python
import asyncio
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng")

async def run():
    results = await ocr.abatch(
        ["scans/page1.png", "scans/page2.png", "scans/page3.png"],
        max_concurrent=2,
    )
    for index, text in enumerate(results, start=1):
        print(index, text[:120])

asyncio.run(run())
```

### List installed OCR languages

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR()
print(ocr.get_supported_languages())
```

## Related Packages

- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Tesseract OCR documentation](https://tesseract-ocr.github.io/)
- [PyTesseract on PyPI](https://pypi.org/project/pytesseract/)
- [Pillow documentation](https://pillow.readthedocs.io/)

## Best Practices

- Use `--psm` and `--oem` options through `config` to match the page layout you
  expect.
- Install the correct `.traineddata` language packs for multilingual OCR.
- Pre-process noisy or skewed scans before OCR to improve extraction quality.
- Use PDF parsers when a PDF already contains embedded text; use OCR when the
  PDF or image is scan-only.

## License

This project is licensed under the Apache-2.0 License.


