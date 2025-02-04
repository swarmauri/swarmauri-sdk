![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_embedding_nmf)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_embedding_nmf)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_embedding_nmf)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_embedding_nmf?label=swarmauri_embedding_nmf&color=green)

</div>

---

# NMF Embedding Package

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

