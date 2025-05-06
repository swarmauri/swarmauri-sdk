
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_persistentchromadb/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_persistentchromadb" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_persistentchromadb/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_persistentchromadb.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_persistentchromadb/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_persistentchromadb" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_persistentchromadb/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_persistentchromadb" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_persistentchromadb/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_persistentchromadb?label=swarmauri_vectorstore_persistentchromadb&color=green" alt="PyPI - swarmauri_vectorstore_persistentchromadb"/></a>
</p>

---

# Swarmauri Vectorstore Persistentchromadb

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

