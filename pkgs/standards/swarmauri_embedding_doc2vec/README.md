
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_embedding_doc2vec" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_doc2vec/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_doc2vec.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_embedding_doc2vec" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_doc2vec" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_doc2vec?label=swarmauri_embedding_doc2vec&color=green" alt="PyPI - swarmauri_embedding_doc2vec"/></a>
</p>

---

# Swarmauri Embedding Doc2vec

A Gensim-based Doc2Vec implementation for document embedding in the Swarmauri ecosystem. This package provides document vectorization capabilities using the Doc2Vec algorithm.

## Installation

```bash
pip install swarmauri_embedding_doc2vec
```

## Usage

```python
from swarmauri.embeddings.Doc2VecEmbedding import Doc2VecEmbedding

# Initialize the embedder
embedder = Doc2VecEmbedding(vector_size=3000)

# Prepare your documents
documents = ["This is the first document.", "Here is another document.", "And a third one"]

# Fit and transform documents
vectors = embedder.fit_transform(documents)

# Transform new documents
new_doc = "This is a new document"
vector = embedder.transform([new_doc])

# Save and load the model
embedder.save_model("doc2vec.model")
embedder.load_model("doc2vec.model")
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
