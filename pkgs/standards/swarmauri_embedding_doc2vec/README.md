![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_embedding_doc2vec/">
        <img src="https://static.pepy.tech/badge/swarmauri_embedding_doc2vec/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_doc2vec/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_embedding_doc2vec.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/l/swarmauri_embedding_doc2vec" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_embedding_doc2vec/">
        <img src="https://img.shields.io/pypi/v/swarmauri_embedding_doc2vec?label=swarmauri_embedding_doc2vec&color=green" alt="PyPI - swarmauri_embedding_doc2vec"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Embedding Doc2vec

A [Gensim](https://radimrehurek.com/gensim/)-powered Doc2Vec implementation for document
embeddings in the Swarmauri ecosystem. The component registers as
`Doc2VecEmbedding` and returns vectors as `swarmauri_standard.vectors.Vector`
instances.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_embedding_doc2vec
```

```bash
poetry add swarmauri_embedding_doc2vec
```

```bash
uv pip install swarmauri_embedding_doc2vec
```

## Usage

```python
from swarmauri_embedding_doc2vec import Doc2VecEmbedding

documents = [
    "This is the first document.",
    "Here is another document.",
    "And a third one.",
]

# Initialize the embedder. Adjust parameters to match your dataset size.
embedder = Doc2VecEmbedding(vector_size=300, window=10, min_count=1, workers=1)

# Fit and transform documents into Vector objects.
vectors = embedder.fit_transform(documents)

# Access the raw embedding values via the Vector.value attribute.
first_vector = vectors[0].value

# Transform new documents (the result is also a Vector).
new_vector = embedder.transform(["This is a new document."])[0]

# Save and load the underlying Doc2Vec model.
model_path = "doc2vec.model"
embedder.save_model(model_path)
embedder.load_model(model_path)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


