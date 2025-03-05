
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_neo4j/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_neo4j" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_vectorstore_neo4j/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_vectorstore_neo4j/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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

