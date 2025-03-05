
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_parser_bertembedding/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_parser_bertembedding" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_bertembedding/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_parser_bertembedding/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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
