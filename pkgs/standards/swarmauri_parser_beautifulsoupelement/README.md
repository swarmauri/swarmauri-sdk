
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_beautifulsoupelement" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_beautifulsoupelement/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_beautifulsoupelement.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_beautifulsoupelement" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_beautifulsoupelement" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_beautifulsoupelement/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_beautifulsoupelement?label=swarmauri_parser_beautifulsoupelement&color=green" alt="PyPI - swarmauri_parser_beautifulsoupelement"/></a>
</p>

---

# Swarmauri Parser Beautifulsoupelement

A specialized parser that utilizes BeautifulSoup to extract specific HTML elements and their content from HTML documents.

## Installation

```bash
pip install swarmauri_parser_beautifulsoupelement
```

## Usage

The BeautifulSoupElementParser allows you to extract specific HTML elements from HTML content:

```python
from swarmauri_parser_beautifulsoupelement.BeautifulSoupElementParser import BeautifulSoupElementParser

# Create a parser instance to extract paragraphs
parser = BeautifulSoupElementParser(element="p")

# HTML content to parse
html_content = "<div><p>First paragraph</p><p>Second paragraph</p></div>"

# Parse the content
documents = parser.parse(html_content)

# Access the extracted elements
for doc in documents:
    print(doc.content)  # Prints each paragraph element
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
