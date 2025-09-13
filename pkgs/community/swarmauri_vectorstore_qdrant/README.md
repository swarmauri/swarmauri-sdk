
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_qdrant" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_qdrant/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_qdrant.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_qdrant" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_qdrant" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_qdrant?label=swarmauri_vectorstore_qdrant&color=green" alt="PyPI - swarmauri_vectorstore_qdrant"/></a>
</p>

---

# Swarmauri Vectorstore Qdrant

A vector store implementation using Qdrant as the backend, supporting both persistent local storage and cloud-based operations for document storage and retrieval.

## Installation

```bash
pip install swarmauri_vectorstore_qdrant
```

## Usage

```python
from swarmauri.documents.Document import Document
from swarmauri.vectorstores.PersistentQdrantVectorStore import PersistentQdrantVectorStore
from swarmauri.vector_stores.CloudQdrantVectorStore import CloudQdrantVectorStore

# Local Persistent Storage
local_store = PersistentQdrantVectorStore(
    collection_name="my_collection",
    vector_size=100,
    path="http://localhost:6333"
)
local_store.connect()

# Cloud Storage
cloud_store = CloudQdrantVectorStore(
    api_key="your_api_key",
    collection_name="my_collection",
    vector_size=100,
    url="your_qdrant_cloud_url"
)
cloud_store.connect()

# Add documents
documents = [
    Document(content="sample text 1"),
    Document(content="sample text 2")
]
local_store.add_documents(documents)

# Retrieve similar documents
results = local_store.retrieve("sample query", top_k=5)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
