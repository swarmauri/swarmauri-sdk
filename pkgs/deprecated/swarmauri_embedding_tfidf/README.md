
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_tfidf" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_tfidf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_tfidf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_tfidf" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_tfidf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_tfidf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_tfidf?label=swarmauri_embedding_tfidf&color=green" alt="PyPI - swarmauri_embedding_tfidf"/></a>
</p>

---

# Swarmauri Embedding TFIDF

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
