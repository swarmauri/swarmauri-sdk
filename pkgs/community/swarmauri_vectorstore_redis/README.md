![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_redis)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_redis)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_redis)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_redis?label=swarmauri_vectorstore_redis&color=green)

</div>

---

# Redis Vector Store for Swarmauri

A Redis-based vector store implementation for the Swarmauri SDK that enables efficient storage and retrieval of document embeddings.

## Installation

```bash
pip install swarmauri_vectorstore_redis
```

## Usage

Basic example of using RedisVectorStore:

```python
from swarmauri.vector_stores.RedisVectorStore import RedisVectorStore
from swarmauri.documents.Document import Document

# Initialize the vector store
vector_store = RedisVectorStore(
    redis_host="localhost",
    redis_port=6379,
    redis_password="your_password",
    embedding_dimension=8000
)

# Add documents
document = Document(
    id="doc1",
    content="Sample document content",
    metadata={"category": "sample"}
)
vector_store.add_document(document)

# Retrieve similar documents
similar_docs = vector_store.retrieve("sample content", top_k=5)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

