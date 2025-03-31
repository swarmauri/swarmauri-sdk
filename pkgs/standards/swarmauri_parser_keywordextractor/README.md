
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_keywordextractor" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_parser_keywordextractor/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_parser_keywordextractor/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_keywordextractor" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_keywordextractor" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_keywordextractor?label=swarmauri_parser_keywordextractor&color=green" alt="PyPI - swarmauri_parser_keywordextractor"/></a>
</p>

---

# Swarmauri Parser Keywordextractor

A parser component that extracts keywords from text using the YAKE keyword extraction library.

## Installation

```bash
pip install swarmauri_parser_keywordextractor
```

## Usage
Here's a basic example of how to use the KeywordExtractorParser:
```python
from swarmauri_parser_keywordextractor.KeywordExtractorParser import KeywordExtractorParser

# Initialize the parser
parser = KeywordExtractorParser()

# Parse text and extract keywords
text = "Artificial intelligence and machine learning are transforming technology"
documents = parser.parse(text)

# Access extracted keywords and their scores
for doc in documents:
    print(f"Keyword: {doc.content}, Score: {doc.metadata['score']}")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

