
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_tfidf" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_embedding_tfidf/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_embedding_tfidf/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_tfidf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_tfidf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_tfidf?label=swarmauri_embedding_tfidf&color=green" alt="PyPI - swarmauri_embedding_tfidf"/></a>
</p>

---

# Swarmauri Embedding Tfidf

A TF-IDF (Term Frequency-Inverse Document Frequency) embedding implementation for the Swarmauri SDK, providing document vectorization capabilities.

## Installation

```bash
pip install swarmauri_embedding_tfidf
```

## Usage

```python
from swarmauri_embedding_tfidf.TfidfEmbedding import TfidfEmbedding

# Initialize the embedder
embedder = TfidfEmbedding()

# Prepare documents
documents = ["this is a sample", "another example text", "third document here"]

# Fit and transform documents
vectors = embedder.fit_transform(documents)

# Infer vector for new text
query_vector = embedder.infer_vector("new document", documents)

# Extract features
features = embedder.extract_features()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
