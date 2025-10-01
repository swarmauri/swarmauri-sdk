![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_downloadpdf" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_downloadpdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_downloadpdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_downloadpdf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_downloadpdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_downloadpdf?label=swarmauri_tool_downloadpdf&color=green" alt="PyPI - swarmauri_tool_downloadpdf"/></a>
</p>

---

# Swarmauri Tool Download PDF

Tool that downloads a PDF by URL and returns the file contents as a base64-encoded string, enabling downstream storage or inline embedding without touching disk.

## Features

- Uses `requests` to stream PDF bytes.
- Encodes the result into base64 (`content` field) and includes a success message.
- Returns an `error` key when download or processing fails.

## Prerequisites

- Python 3.10 or newer.
- `requests` (installed automatically).
- Network access to the target PDF URL.

## Installation

```bash
# pip
pip install swarmauri_tool_downloadpdf

# poetry
poetry add swarmauri_tool_downloadpdf

# uv (pyproject-based projects)
uv add swarmauri_tool_downloadpdf
```

## Quickstart

```python
import base64
from pathlib import Path
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

if "error" in result:
    print(result["error"])
else:
    pdf_bytes = base64.b64decode(result["content"])
    Path("downloaded.pdf").write_bytes(pdf_bytes)
```

## Tips

- Always check for the `error` key before assuming the download succeeded.
- Large PDFs load into memory—consider chunking or alternative tools if you need to stream huge files directly to disk.
- Validate URLs to avoid downloading untrusted content when wiring this tool into automated pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
