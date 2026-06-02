![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_vectorstore_fs/">
        <img src="https://static.pepy.tech/badge/swarmauri_vectorstore_fs/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_fs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_fs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_fs/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_fs/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_fs" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_fs/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_fs?label=swarmauri_vectorstore_fs&color=green" alt="PyPI - swarmauri_vectorstore_fs"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Vectorstore FS

A Swarmauri community vector store that indexes filesystem trees for BM25F retrieval over file paths, file names, extensions, chunk identity, and file content.

## Features

- Filesystem-aware retrieval with weighted BM25F fields
- Chunk, file, and chunk-plus-file indexing modes
- Stable chunk identity metadata for global, path-level, and file-level chunk numbering
- CLI for ad hoc lexical search over source trees and document corpora
- No embedding vocabulary dependency for query handling

## Installation

```bash
pip install swarmauri_vectorstore_fs
```

## Usage

```python
from swarmauri_vectorstore_fs import FsVectorStore

store = FsVectorStore(root_path=".", mode="chunk")
store.build_index()
results = store.retrieve("vector store registration", top_k=3)

for document in results:
    print(document.id, document.metadata["relative_path"])
```

## CLI

```bash
fsvs --root . query --query "vector store registration" --top-k 5
```

To inspect a specific retrieved document:

```bash
fsvs --root . show --document-id <document-id>
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).


