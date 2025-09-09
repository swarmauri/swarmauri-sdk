
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_nmf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_nmf" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_nmf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_nmf.svg"/></a>
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

