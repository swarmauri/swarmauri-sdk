![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_annoy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_annoy)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_annoy)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_annoy?label=swarmauri_vectorstore_annoy&color=green)

</div>

---

# Annoy Vector Store

A vector store implementation using Annoy as the backend for efficient similarity search and nearest neighbor queries.

## Installation

```bash
pip install swarmauri_vectorstore_annoy
```

## Usage

```python
from swarmauri.vector_stores.AnnoyVectorStore import AnnoyVectorStore
from swarmauri_standard.documents.Document import Document

# Initialize vector store
vector_store = AnnoyVectorStore(
    collection_name="my_collection",
    vector_size=100
)
vector_store.connect()

# Add documents
documents = [
    Document(content="first document"),
    Document(content="second document"),
    Document(content="third document")
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
