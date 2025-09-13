
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_redis/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_redis" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_redis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_redis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_redis/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_redis" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_redis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_redis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_redis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_redis?label=swarmauri_vectorstore_redis&color=green" alt="PyPI - swarmauri_vectorstore_redis"/></a>
</p>

---

# Swarmauri Vectorstore Redis

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

