
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_textblob/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_textblob" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_textblob/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_textblob.svg"/></a>
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
