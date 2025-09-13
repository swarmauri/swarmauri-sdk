
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_mlm/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_mlm" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_mlm/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_mlm.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_mlm/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_mlm" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_mlm/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_mlm" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_mlm/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_mlm?label=swarmauri_vectorstore_mlm&color=green" alt="PyPI - swarmauri_vectorstore_mlm"/></a>
</p>

---

# Swarmauri Vectorstore Mlm

A vector store implementation using MLM (Masked Language Model) embeddings for document storage and retrieval.

## Installation

```bash
pip install swarmauri_vectorstore_mlm
```

## Usage

Here's a basic example of how to use the MLM Vector Store:

```python
from swarmauri.documents.Document import Document
from swarmauri.vector_stores.MlmVectorStore import MlmVectorStore

# Initialize the vector store
vs = MlmVectorStore()

# Create some documents
documents = [
    Document(content="first document"),
    Document(content="second document"),
    Document(content="third document")
]

# Add documents to the store
vs.add_documents(documents)

# Retrieve similar documents
results = vs.retrieve(query="document", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

