![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_downloadpdf)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_downloadpdf)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_downloadpdf)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_downloadpdf?label=swarmauri_tool_downloadpdf&color=green)

</div>

---

# Swarmauri Tool DownloadPDF

A tool to download a PDF from a specified URL and save it to a specified path.

## Installation

```bash
pip install swarmauri_tool_downloadpdf
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.tools.DownloadPdfTool import DownloadPDFTool

tool = DownloadPDFTool()
url = "http://example.com/sample.pdf"
result = tool(url)

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Message: {result['message']}")
    print(f"Content: {result['content']}")
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
