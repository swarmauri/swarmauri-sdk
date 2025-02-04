![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_mlm)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_mlm)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_mlm)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_mlm?label=swarmauri_vectorstore_mlm&color=green)

</div>

---

# MLM Vector Store

A vector store implementation using MLM (Masked Language Model) embeddings for document storage and retrieval.

## Installation

```bash
pip install swarmauri_vectorstore_mlm
```

## Usage

Here's a basic example of how to use the MLM Vector Store:

```python
from swarmauri.documents.Document import Document
from swarmauri.vector_stores.MlmVectorStore import MlmVectorStore

# Initialize the vector store
vs = MlmVectorStore()

# Create some documents
documents = [
    Document(content="first document"),
    Document(content="second document"),
    Document(content="third document")
]

# Add documents to the store
vs.add_documents(documents)

# Retrieve similar documents
results = vs.retrieve(query="document", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

