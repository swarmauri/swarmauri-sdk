
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_textblob" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_textblob/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_parser_textblob/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_textblob" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_textblob" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_textblob?label=swarmauri_parser_textblob&color=green" alt="PyPI - swarmauri_parser_textblob"/></a>
</p>

---

# Swarmauri Parser TextBlob

A parser package that leverages TextBlob for natural language processing tasks such as sentence parsing and noun phrase extraction.

## Installation

```bash
pip install swarmauri_parser_textblob
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.TextBlobSentenceParser import TextBlobSentenceParser
from swarmauri.parsers.TextBlobNounParser import TextBlobNounParser

# Example usage of TextBlobSentenceParser
sentence_parser = TextBlobSentenceParser()
sentences = sentence_parser.parse("One more large chapula please.")
for doc in sentences:
    print(doc.content)

# Example usage of TextBlobNounParser
noun_parser = TextBlobNounParser()
documents = noun_parser.parse("One more large chapula please.")
for doc in documents:
    print(doc.content)
    print(doc.metadata["noun_phrases"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
