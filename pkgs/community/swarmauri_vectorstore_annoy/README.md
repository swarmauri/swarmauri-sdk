
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_annoy/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_annoy" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_annoy/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_annoy.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_annoy/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_annoy" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_annoy/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_annoy" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_annoy/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_annoy?label=swarmauri_vectorstore_annoy&color=green" alt="PyPI - swarmauri_vectorstore_annoy"/></a>
</p>

---

# Swarmauri VectorStore Annoy

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
