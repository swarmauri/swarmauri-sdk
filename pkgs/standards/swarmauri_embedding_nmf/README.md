
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_nmf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_nmf" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_embedding_nmf/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_embedding_nmf/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_nmf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_nmf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_nmf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_nmf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_nmf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_nmf?label=swarmauri_embedding_nmf&color=green" alt="PyPI - swarmauri_embedding_nmf"/></a>
</p>

---

# Swarmauri Embedding Nmf

A Non-negative Matrix Factorization (NMF) based embedding implementation for text data processing in the Swarmauri ecosystem.

## Installation

```bash
pip install swarmauri_embedding_nmf
```

## Usage
Here's a basic example of how to use the NMF Embedding:

```python
from swarmauri.embeddings.NmfEmbedding import NmfEmbedding

# Initialize the embedder
embedder = NmfEmbedding(n_components=10)

# Example documents
documents = ["This is the first document", "This is the second document", "And this is the third one"]

# Fit and transform the documents
vectors = embedder.fit_transform(documents)

# Transform a new document
new_vector = embedder.infer_vector("This is a new document")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

