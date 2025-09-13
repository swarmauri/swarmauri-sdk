
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_mlm" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_embedding_mlm.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_mlm" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_mlm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_mlm/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_mlm?label=swarmauri_embedding_mlm&color=green" alt="PyPI - swarmauri_embedding_mlm"/></a>
</p>

---

# Swarmauri Embedding MLM

This package provides an implementation of an embedding model that fine-tunes a Masked Language Model (MLM) for generating embeddings.

## Installation

```bash
pip install swarmauri_embedding_mlm
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.embeddings.MlmEmbedding import MlmEmbedding

# Initialize the embedder
embedder = MlmEmbedding()

# Fit the model on a list of documents
documents = ["This is a test document.", "Another document for embedding."]
embedder.fit(documents)

# Transform documents to embeddings
embeddings = embedder.transform(documents)

# Save the model
embedder.save_model("path/to/save/model")

# Load the model
embedder.load_model("path/to/save/model")

# Infer vector for a single document
vector = embedder.infer_vector("This is a new document.")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

