
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_doc2vec/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_doc2vec" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_vectorstore_doc2vec/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_vectorstore_doc2vec.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_doc2vec/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_doc2vec" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_doc2vec/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_doc2vec" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_doc2vec/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_doc2vec?label=swarmauri_vectorstore_doc2vec&color=green" alt="PyPI - swarmauri_vectorstore_doc2vec"/></a>
</p>

---

# Swarmauri Vectorstore Doc2vec

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

