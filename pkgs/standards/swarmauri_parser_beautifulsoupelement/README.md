![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_parser_beautifulsoupelement)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_parser_beautifulsoupelement)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_parser_beautifulsoupelement)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_parser_beautifulsoupelement?label=swarmauri_parser_beautifulsoupelement&color=green)

</div>

---

# BeautifulSoup Element Parser

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
