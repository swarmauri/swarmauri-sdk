
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_cloudweaviate/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_cloudweaviate" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_cloudweaviate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_cloudweaviate.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_cloudweaviate/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_cloudweaviate" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_cloudweaviate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_cloudweaviate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_cloudweaviate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_cloudweaviate?label=swarmauri_vectorstore_cloudweaviate&color=green" alt="PyPI - swarmauri_vectorstore_cloudweaviate"/></a>
</p>

---

# Swarmauri Vectorstore CloudWeaviate

A Weaviate-based vector store implementation for Swarmauri, providing cloud-based document storage and retrieval with vector similarity search capabilities.

## Installation

```bash
pip install swarmauri_vectorstore_cloudweaviate
```

## Usage
Here's a basic example of how to use the CloudWeaviateVectorStore:

```python
from swarmauri.vector_stores.CloudWeaviateVectorStore import CloudWeaviateVectorStore
from swarmauri.documents.Document import Document

# Initialize the vector store
vector_store = CloudWeaviateVectorStore(
    url="your-weaviate-url",
    api_key="your-api-key",
    collection_name="example",
    vector_size=100
)

# Connect to Weaviate
vector_store.connect()

# Add documents
document = Document(
    id="doc-001",
    content="This is a sample document content.",
    metadata={"author": "Alice", "date": "2024-01-01"}
)
vector_store.add_document(document)

# Retrieve similar documents
results = vector_store.retrieve(query="sample content", top_k=5)

# Clean up
vector_store.disconnect()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

