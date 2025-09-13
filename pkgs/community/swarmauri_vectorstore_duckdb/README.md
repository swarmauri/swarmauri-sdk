
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_duckdb/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_duckdb" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_duckdb/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_duckdb.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_duckdb/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_duckdb" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_duckdb/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_duckdb" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_duckdb/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_duckdb?label=swarmauri_vectorstore_duckdb&color=green" alt="PyPI - swarmauri_vectorstore_duckdb"/></a>
</p>

---

# Swarmauri Vectorstore Duckdb

A vector store implementation using DuckDB as the backend for efficient document storage and similarity search.

## Installation

```bash
pip install swarmauri_vectorstore_duckdb
```

## Usage

```python
from swarmauri.vector_stores.DuckDBVectorStore import DuckDBVectorStore
from swarmauri.documents.Document import Document

# Initialize vector store
vector_store = DuckDBVectorStore(database_name="my_vectors.db")
vector_store.connect()

# Add documents
doc = Document(
    id="doc1",
    content="The quick brown fox jumps over the lazy dog",
    metadata={"type": "example"}
)
vector_store.add_document(doc)

# Retrieve similar documents
results = vector_store.retrieve("fox jumping", top_k=2)

# Clean up
vector_store.disconnect()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

