
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_webscraping" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_webscraping/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_webscraping.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_webscraping" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_webscraping" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_webscraping?label=swarmauri_tool_webscraping&color=green" alt="PyPI - swarmauri_tool_webscraping"/></a>
</p>

---

# Swarmauri Tool Web Scraping

A web scraping tool that uses Python's requests and BeautifulSoup libraries to parse web content using CSS selectors.

## Installation

```bash
pip install swarmauri_tool_webscraping
```

## Usage

```python
from swarmauri.tools.WebScrapingTool import WebScrapingTool

# Initialize the tool
scraper = WebScrapingTool()

# Scrape content from a webpage
result = scraper(
    url="https://example.com",
    selector="h1"
)

# Access the extracted text
if "extracted_text" in result:
    print(result["extracted_text"])
else:
    print(result["error"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
