![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_vectorstore_tfidf/">
        <img src="https://static.pepy.tech/badge/swarmauri_vectorstore_tfidf/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_vectorstore_tfidf/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_vectorstore_tfidf.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_tfidf/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_tfidf/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_tfidf" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_tfidf/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_tfidf?label=swarmauri_vectorstore_tfidf&color=green" alt="PyPI - swarmauri_vectorstore_tfidf"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Vectorstore Tfidf

A vector store implementation using TF-IDF (Term Frequency-Inverse Document Frequency) for document embedding and retrieval. This package provides efficient document storage and similarity-based retrieval using the TF-IDF algorithm.

## Installation

```bash
pip install swarmauri_vectorstore_tfidf
```

## Usage

Here's a basic example of how to use the TF-IDF Vector Store:

```python
from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
from swarmauri.documents.Document import Document

# Initialize the vector store
vector_store = TfidfVectorStore()

# Add documents
documents = [
    Document(content="Machine learning basics"),
    Document(content="Python programming guide"),
    Document(content="Data science tutorial")
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="python tutorial", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.


