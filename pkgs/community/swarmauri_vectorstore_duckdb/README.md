![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_duckdb)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_duckdb)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_duckdb)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_duckdb?label=swarmauri_vectorstore_duckdb&color=green)

</div>

---

# DuckDB Vector Store

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

