![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_persistentchromadb)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_persistentchromadb)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_persistentchromadb)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_persistentchromadb?label=swarmauri_vectorstore_persistentchromadb&color=green)

</div>

---

# Persistent ChromaDB Vector Store

A persistent vector store implementation using ChromaDB for document storage and retrieval with embeddings.

## Installation

```bash
pip install swarmauri_vectorstore_persistentchromadb
```

## Usage

```python
from swarmauri.documents.Document import Document
from swarmauri.vector_stores.PersistentChromaDBVectorStore import PersistentChromaDBVectorStore

# Initialize the vector store
vector_store = PersistentChromaDBVectorStore(
    path="./chromadb_data",
    collection_name="my_collection",
    vector_size=100
)

# Connect to the store
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

