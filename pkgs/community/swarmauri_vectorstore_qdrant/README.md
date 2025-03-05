
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_qdrant" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_vectorstore_qdrant/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_vectorstore_qdrant/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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
