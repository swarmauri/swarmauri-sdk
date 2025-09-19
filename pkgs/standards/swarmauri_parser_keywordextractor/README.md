
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_keywordextractor" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_keywordextractor/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_parser_keywordextractor.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_keywordextractor" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_keywordextractor" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_keywordextractor/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_keywordextractor?label=swarmauri_parser_keywordextractor&color=green" alt="PyPI - swarmauri_parser_keywordextractor"/></a>
</p>

---

# Swarmauri Parser Keywordextractor

`KeywordExtractorParser` wraps the [YAKE](https://github.com/LIAAD/yake) keyword
extraction library to turn arbitrary text into a ranked list of
`swarmauri_standard.documents.Document` instances. Each returned document stores
the detected keyword in `content` and the YAKE importance score in
`metadata["score"]`.

The parser normalizes any input into a string before analysis and, by default,
extracts up to 10 keywords using the English language model, three-word maximum
phrases, and YAKE's sequence-matching deduplication (`dedupLim=0.9`). Override
`lang` or `num_keywords` when instantiating the parser to tailor the output to
your dataset.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_parser_keywordextractor

# Poetry
poetry add swarmauri_parser_keywordextractor

# uv
uv add swarmauri_parser_keywordextractor
```

## Usage

Here's a basic example of how to use the `KeywordExtractorParser`:

```python
from swarmauri_parser_keywordextractor import KeywordExtractorParser

# Initialize the parser for three keywords in English
parser = KeywordExtractorParser(num_keywords=3, lang="en")

text = "Artificial intelligence and machine learning are transforming technology"
documents = parser.parse(text)

for document in documents:
    score = document.metadata["score"]
    print(f"Keyword: {document.content}, Score: {score:.4f}")
```

Each call to `parse` returns a list of `Document` objects ranked by YAKE so you
can feed them directly into downstream Swarmauri pipelines.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

