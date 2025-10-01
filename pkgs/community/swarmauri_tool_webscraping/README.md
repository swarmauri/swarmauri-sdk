![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

# Swarmauri Tool · Web Scraping

A Swarmauri-compatible scraper that fetches HTML with `requests`, parses it via BeautifulSoup, and extracts content with CSS selectors. Ideal for lightweight data collection, compliance checks, or enriching agent answers with live webpage snippets.

- Accepts any valid URL and CSS selector; returns joined text content from the matching nodes.
- Handles HTTP/network failures gracefully by surfacing structured error messages.
- Integrates with Swarmauri agents so scraping can be triggered through natural-language prompts.

## Requirements

- Python 3.10 – 3.13.
- `requests` and `beautifulsoup4` (installed automatically with the package).
- Respect site terms of service, robots.txt directives, and rate limits when scraping.

## Installation

Use your preferred packaging workflow—each command installs the dependencies above.

**pip**

```bash
pip install swarmauri_tool_webscraping
```

**Poetry**

```bash
poetry add swarmauri_tool_webscraping
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_webscraping

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_webscraping
```

> Tip: In containerized or restricted environments ensure outbound HTTPS traffic is permitted; `requests` needs network access to reach target sites.

## Quick Start

```python
from swarmauri_tool_webscraping import WebScrapingTool

scraper = WebScrapingTool()
result = scraper(url="https://example.com", selector="h1")

if "extracted_text" in result:
    print(result["extracted_text"])
else:
    print(result["error"])
```

`extracted_text` concatenates matches separated by newlines. When no elements match the selector, the tool returns an empty string.

## Usage Scenarios

### Monitor Site Copy for Compliance

```python
from swarmauri_tool_webscraping import WebScrapingTool

scraper = WebScrapingTool()
result = scraper(
    url="https://status.vendor.com",
    selector=".uptime-banner"
)

if "error" in result:
    raise RuntimeError(result["error"])

if "maintenance" in result["extracted_text"].lower():
    print("Maintenance notice detected – alert the ops team.")
```

### Inject Live Data Into a Swarmauri Agent Response

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_webscraping import WebScrapingTool

registry = ToolRegistry()
registry.register(WebScrapingTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="Check the headline on https://example.com")
response = agent.run(message)
print(response)
```

### Batch Collect Headlines From Multiple Pages

```python
from swarmauri_tool_webscraping import WebScrapingTool

scraper = WebScrapingTool()
urls = [
    "https://news.example.com/tech",
    "https://news.example.com/business",
]

for url in urls:
    result = scraper(url=url, selector="h2.article-title")
    print(url)
    print(result.get("extracted_text", result.get("error")))
    print("---")
```

## Troubleshooting

- **`Request error`** – Network failures, DNS issues, or HTTP 4xx/5xx responses produce `Request error` messages. Verify connectivity, headers, or authentication if required by the site.
- **Empty `extracted_text`** – The selector may not match any nodes. Use browser dev tools to confirm the CSS selector or adjust the parser to target the correct element.
- **SSL certificate problems** – Pass `verify=False` by forking/extending the tool only when you trust the target; otherwise update CA certificates on the host.

## License

`swarmauri_tool_webscraping` is released under the Apache 2.0 License. See `LICENSE` for full details.
