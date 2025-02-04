![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_vectorstore_doc2vec)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_doc2vec)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_vectorstore_doc2vec)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_vectorstore_doc2vec?label=swarmauri_vectorstore_doc2vec&color=green)

</div>

---

# Doc2Vec Vector Store

A vector store implementation using Doc2Vec for document embedding and similarity search.

## Installation

```bash
pip install swarmauri_vectorstore_doc2vec
```

## Usage

```python
from swarmauri.vectorstores.Doc2VecVectorStore import Doc2VecVectorStore
from swarmauri.documents.Document import Document


# Initialize vector store
vector_store = Doc2VecVectorStore()

# Add documents
documents = [
    Document(content="This is the first document"),
    Document(content="Here is another document"),
    Document(content="And a third document")
]
vector_store.add_documents(documents)

# Retrieve similar documents
results = vector_store.retrieve(query="document", top_k=2)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

