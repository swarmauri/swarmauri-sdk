![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_pinecone)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_pinecone)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_pinecone)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_pinecone?label=swarmauri_vectorstore_pinecone&color=green)

</div>

---

# Swarmauri Pinecone Vector Store

A vector store implementation using Pinecone as the backend for efficient similarity search and document storage.

## Installation

```bash
pip install swarmauri_vectorstore_pinecone
```

## Usage

```python
from swarmauri.vector_stores.PineconeVectorStore import PineconeVectorStore
from swarmauri.documents.Document import Document

# Initialize vector store
vector_store = PineconeVectorStore(
    api_key="your-pinecone-api-key",
    collection_name="example",
    vector_size=100
)
vector_store.connect()

# Add documents
documents = [
    Document(content="First document"),
    Document(content="Second document"),
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
