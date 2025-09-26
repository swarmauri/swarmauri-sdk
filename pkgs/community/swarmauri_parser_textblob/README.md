![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

TextBlob-backed parsers for Swarmauri that split text into sentences or extract noun phrases. Ships two components: `TextBlobSentenceParser` and `TextBlobNounParser`.

## Features

- Sentence parser returns a `Document` per sentence with metadata identifying the parser.
- Noun phrase parser returns the original text plus `metadata['noun_phrases']` containing the phrases discovered by TextBlob.
- Auto-downloads required NLTK corpora (`punkt_tab`) during initialization.

## Prerequisites

- Python 3.10 or newer.
- [TextBlob](https://textblob.readthedocs.io/) and its NLTK dependencies (installed automatically).
- Internet access on first run so NLTK can download tokenizer data (or pre-download via `python -m textblob.download_corpora`).

## Installation

```bash
# pip
pip install swarmauri_parser_textblob

# poetry
poetry add swarmauri_parser_textblob

# uv (pyproject-based projects)
uv add swarmauri_parser_textblob
```

## Sentence Parsing

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
text = "One more large chapula please. It should be extra spicy!"

sentences = parser.parse(text)
for doc in sentences:
    print(doc.content)
```

## Noun Phrase Extraction

```python
from swarmauri_parser_textblob import TextBlobNounParser

parser = TextBlobNounParser()
docs = parser.parse("One more large chapula please.")

for doc in docs:
    print(doc.content)
    print(doc.metadata["noun_phrases"])
```

## Tips

- TextBlob uses simple heuristics—it works well for general English text but may struggle with domain-specific jargon.
- Download corpora once in CI/CD or container builds (`python -m textblob.download_corpora`) to avoid runtime downloads.
- Combine sentence and noun parsers to build structured representations of documents before vectorization or downstream NLP tasks.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
