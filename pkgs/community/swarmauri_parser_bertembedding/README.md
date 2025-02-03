![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri-parser-bertembedding)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri-parser-bertembedding)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri-parser-bertembedding)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri-parser-bertembedding?label=swarmauri-parser-bertembedding&color=green)

</div>

---

# Swarmauri BERT Embedding Parser

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
