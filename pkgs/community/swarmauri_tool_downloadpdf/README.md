![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_downloadpdf/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_downloadpdf/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_downloadpdf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_downloadpdf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_downloadpdf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_downloadpdf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_downloadpdf?label=swarmauri_tool_downloadpdf&color=green" alt="PyPI - swarmauri_tool_downloadpdf"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Download PDF

`swarmauri_tool_downloadpdf` is a Swarmauri document-ingestion tool for
fetching a PDF from a URL and returning its contents as a base64-encoded
string. It is useful for agent workflows, document capture, API handoffs, and
pipelines that need PDF content in memory without writing directly to disk.

## Why Use Swarmauri Tool Download PDF

- Retrieve PDFs from remote URLs inside Swarmauri workflows.
- Keep document transfer in-memory with base64 output.
- Hand off downloaded PDF content to parsers, storage layers, or APIs.
- Surface structured success or error responses from HTTP downloads.

## FAQ

> **What does the tool return on success?**  
> A dictionary with `message` and base64-encoded `content`.

> **Does it save files to disk?**  
> No. It downloads bytes into memory and returns them encoded as base64.

> **What input does it expect?**  
> The callable runtime surface currently expects a single `url` string.

> **How are download failures reported?**  
> The tool returns an `error` key with a descriptive message.

## Features

- Swarmauri `ToolBase` implementation registered as `DownloadPDFTool`.
- Fetches PDF bytes with `requests`.
- Returns PDF content as base64 for easy transport.
- Avoids filesystem writes in the default flow.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_downloadpdf
```

```bash
pip install swarmauri_tool_downloadpdf
```

## Usage

```python
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

print(result.keys())
```

## Examples

### Decode the returned PDF payload

```python
import base64
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://example.com/report.pdf")

if "content" in result:
    pdf_bytes = base64.b64decode(result["content"])
    print(len(pdf_bytes))
```

### Send PDF content to another API

```python
import requests
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://example.com/form.pdf")

if "content" in result:
    requests.post("https://api.example.com/upload", json=result)
```

### Use the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_downloadpdf import DownloadPDFTool

tools = ToolCollection(tools=[DownloadPDFTool()])
print(tools)
```

## Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_tool_webscraping](https://pypi.org/project/swarmauri_tool_webscraping/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Requests documentation](https://requests.readthedocs.io/)
- [Base64 encoding in Python](https://docs.python.org/3/library/base64.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Validate and sanitize URLs before downloading untrusted documents.
- Guard against large PDFs if memory pressure matters in your runtime.
- Check for `error` before decoding returned content.
- Hand base64 output directly to downstream services when possible to avoid
  unnecessary temporary files.

## License

This project is licensed under the Apache-2.0 License.
