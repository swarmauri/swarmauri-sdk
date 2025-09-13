
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_bertembedding" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_bertembedding.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_parser_bertembedding" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_bertembedding" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_bertembedding?label=swarmauri_parser_bertembedding&color=green" alt="PyPI - swarmauri_parser_bertembedding"/></a>
</p>

---

# Swarmauri Parser Bert Embedding

A parser that transforms input text into document embeddings using BERT.

## Installation

```bash
pip install swarmauri_parser_bertembedding
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.parsers.BERTEmbeddingParser import BERTEmbeddingParser

# Initialize the parser
parser = BERTEmbeddingParser()

# Parse some text data
documents = parser.parse("Your text data here")

# Access the embeddings
for doc in documents:
    print(doc.content)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
