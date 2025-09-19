
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`swarmauri_embedding_nmf` provides a Non-negative Matrix Factorization (NMF)
implementation that converts collections of documents into dense numeric
vectors. Under the hood it combines `TfidfVectorizer` and `NMF` from
scikit-learn and wraps the results in Swarmauri's [`Vector`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_standard/swarmauri_standard/vectors/Vector.py)
type so the embeddings fit seamlessly into the wider ecosystem.

## Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_embedding_nmf

# Poetry
poetry add swarmauri_embedding_nmf

# uv
uv add swarmauri_embedding_nmf
```

## Quickstart

```python
from swarmauri_embedding_nmf import NmfEmbedding

documents = [
    "This is the first document",
    "This is the second document",
    "And this is the third one",
]

# n_components must not exceed the number of documents or unique terms
embedder = NmfEmbedding(n_components=3)

# Fit and transform the documents into Swarmauri Vector objects
vectors = embedder.fit_transform(documents)

for document, vector in zip(documents, vectors):
    print(document, vector.value)

print("Vocabulary:", embedder.extract_features())

# Transform a new document after fitting
new_vector = embedder.infer_vector("This is a new document")
print("New vector:", new_vector.value)
```

`fit_transform` and `infer_vector` both return `Vector` instances. Access the
numerical data through each vector's `.value` attribute when interacting with
other libraries or serialising results.

### Persisting trained models

After training you can persist the TF-IDF vectoriser and NMF model:

```python
embedder.save_model("nmf_embedding")
embedder.load_model("nmf_embedding")
```

The `save_model` method writes two files with `_tfidf.joblib` and
`_nmf.joblib` suffixes, and `load_model` restores the same components for
future inference sessions.

### Swarmauri plugin usage

Installing this package also registers the
`swarmauri.embeddings.NmfEmbedding` entry point. When you already depend on
the `swarmauri` meta-package you can continue to import the embedder via the
registry:

```python
from swarmauri.embeddings.NmfEmbedding import NmfEmbedding
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

