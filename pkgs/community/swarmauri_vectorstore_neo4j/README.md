
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_neo4j/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_neo4j" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_neo4j/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_neo4j.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_neo4j/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_neo4j" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_neo4j/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_neo4j" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_neo4j/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_neo4j?label=swarmauri_vectorstore_neo4j&color=green" alt="PyPI - swarmauri_vectorstore_neo4j"/></a>
</p>

---

# Swarmauri Vectorstore Neo4j

A Neo4j-based vector store implementation for Swarmauri SDK, providing document storage and retrieval functionality using Neo4j graph database.

## Installation

```bash
pip install swarmauri_vectorstore_neo4j
```

## Usage

```python
from swarmauri.documents.Document import Document
from swarmauri.vector_stores.Neo4jVectorStore import Neo4jVectorStore

# Initialize the vector store
store = Neo4jVectorStore(
    uri="neo4j://localhost:7687",
    user="neo4j",
    password="your_password"
)

# Add a document
doc = Document(
    id="doc1",
    content="Sample content",
    metadata={"author": "John Doe"}
)
store.add_document(doc)

# Retrieve similar documents
similar_docs = store.retrieve(query="sample", top_k=5)

# Close connection when done
store.close()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

