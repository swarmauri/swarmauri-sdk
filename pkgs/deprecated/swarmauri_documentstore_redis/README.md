
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_documentstore_redis" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_documentstore_redis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_documentstore_redis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_documentstore_redis" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_documentstore_redis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_documentstore_redis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_documentstore_redis?label=swarmauri_documentstore_redis&color=green" alt="PyPI - swarmauri_documentstore_redis"/></a>
</p>

---

# Swarmauri Documentstore Redis

A Redis-based document store for Swarmauri SDK.

## Installation

```bash
pip install swarmauri_documentstore_redis
```

## Usage

Basic usage examples with code snippets

```python
from swarmauri.documentstores.RedisDocumentStore import RedisDocumentStore
from swarmauri.documents.Document import Document

# Initialize the RedisDocumentStore
store = RedisDocumentStore(host='localhost', password='yourpassword', port=6379, db=0)

# Create a document
document = Document(id='doc1', content='This is a test document')

# Add the document to the store
store.add_document(document)

# Retrieve the document
retrieved_document = store.get_document('doc1')
print(retrieved_document)

# Update the document
document.content = 'This is an updated test document'
store.update_document('doc1', document)

# Delete the document
store.delete_document('doc1')
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
