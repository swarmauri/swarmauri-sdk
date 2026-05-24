![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_webscraping/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_webscraping/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_webscraping/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_webscraping.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_webscraping" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_webscraping/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_webscraping?label=swarmauri_tool_webscraping&color=green" alt="PyPI - swarmauri_tool_webscraping"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Web Scraping

`swarmauri_tool_webscraping` is a Swarmauri web-content extraction tool that
fetches a page with `requests`, parses HTML with BeautifulSoup, and extracts
text using a CSS selector. It is useful for headline capture, policy checks,
lightweight data extraction, and agent workflows that need webpage content on
demand.

## Why Use Swarmauri Tool Web Scraping

- Extract targeted text from webpages using CSS selectors.
- Add lightweight HTML scraping to Swarmauri agents and automation flows.
- Pull site copy, headlines, notices, or metadata for downstream analysis.
- Return structured extraction or error results without custom scraping glue.

## FAQ

> **What inputs does the tool expect?**  
> A `url` string and a CSS `selector` string.

> **What does the tool return?**  
> Either `{"extracted_text": ...}` or `{"error": ...}`.

> **What happens when no elements match?**  
> The tool returns an empty `extracted_text` string.

> **Does it render JavaScript-driven pages?**  
> No. It only fetches raw HTTP content and parses returned HTML.

## Features

- Swarmauri `ToolBase` implementation registered as `WebScrapingTool`.
- Uses standard CSS selectors to target page elements.
- Returns joined text content across all selector matches.
- Handles request and parsing failures with structured error output.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_webscraping
```

```bash
pip install swarmauri_tool_webscraping
```

## Usage

```python
from swarmauri_tool_webscraping import WebScrapingTool

tool = WebScrapingTool()
result = tool(url="https://example.com", selector="h1")

print(result)
```

## Examples

### Extract a page headline

```python
from swarmauri_tool_webscraping import WebScrapingTool

tool = WebScrapingTool()
result = tool("https://example.com", "h1")

print(result.get("extracted_text"))
```

### Inspect a status banner

```python
from swarmauri_tool_webscraping import WebScrapingTool

tool = WebScrapingTool()
result = tool("https://status.example.com", ".banner")

if "error" not in result:
    print(result["extracted_text"])
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_webscraping import WebScrapingTool

tools = ToolCollection(tools=[WebScrapingTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_downloadpdf](https://pypi.org/project/swarmauri_tool_downloadpdf/)
- [swarmauri_tool_searchword](https://pypi.org/project/swarmauri_tool_searchword/)
- [swarmauri_tool_zapierhook](https://pypi.org/project/swarmauri_tool_zapierhook/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Requests documentation](https://requests.readthedocs.io/)
- [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [MDN CSS selectors reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors)

## Best Practices

- Respect site terms, rate limits, and robots rules before scraping.
- Use stable selectors and expect sites to change their markup over time.
- Prefer dedicated APIs when a provider offers one.
- Extend the tool if you need headers, retries, or authenticated requests.

## License

This project is licensed under the Apache-2.0 License.
