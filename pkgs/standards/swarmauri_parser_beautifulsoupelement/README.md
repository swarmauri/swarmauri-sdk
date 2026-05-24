![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_beautifulsoupelement/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_beautifulsoupelement/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_beautifulsoupelement.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_beautifulsoupelement" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_beautifulsoupelement?label=swarmauri_parser_beautifulsoupelement&color=green" alt="PyPI - swarmauri_parser_beautifulsoupelement"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser Beautifulsoupelement

A specialized parser that utilizes BeautifulSoup to extract specific HTML elements and their content from HTML documents. The parser accepts HTML strings only and produces a list of `Document` objects that capture both the HTML snippet for each matched element and metadata (the element tag and its index within the input).

## Installation

Choose the installation workflow that fits your project:

### pip

```bash
pip install swarmauri_parser_beautifulsoupelement
```

### Poetry

```bash
poetry add swarmauri_parser_beautifulsoupelement
```

### uv

If you have not installed `uv` yet, grab it with the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` is available, add the parser to your environment:

```bash
uv pip install swarmauri_parser_beautifulsoupelement
```

## Usage

The `BeautifulSoupElementParser` allows you to extract specific HTML elements from HTML content:

```python
from swarmauri_parser_beautifulsoupelement import BeautifulSoupElementParser

# Create a parser instance to extract paragraphs
parser = BeautifulSoupElementParser(element="p")

# HTML content to parse
html_content = "<div><p>First paragraph
</p><p>Second paragraph
</p></div>"

# Parse the content (input must be a string)
documents = parser.parse(html_content)

# Access the extracted elements and metadata
for doc in documents:
    print(doc.content)     # Prints each paragraph element, including the surrounding <p> tag
    print(doc.metadata)    # {'element': 'p', 'index': 0}, {'element': 'p', 'index': 1}, ...
```

> **Note:** `BeautifulSoupElementParser.parse` raises a `ValueError` if the provided `data` argument is not a string. Ensure that you pass HTML content as a text string before invoking the parser.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


