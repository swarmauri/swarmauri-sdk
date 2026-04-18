![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_vectorstore_git/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_vectorstore_git" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_git/">
        <img src="https://img.shields.io/pypi/l/swarmauri_vectorstore_git" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_vectorstore_git/">
        <img src="https://img.shields.io/pypi/v/swarmauri_vectorstore_git?label=swarmauri_vectorstore_git&color=green" alt="PyPI - swarmauri_vectorstore_git"/></a>
</p>

---

# Swarmauri Vectorstore Git

A Swarmauri community vector store that indexes Git repositories for semantic retrieval over commits and `git log` style records.

## Features

- Index scopes:
  - `head`: commits reachable from `HEAD`
  - `ref`: commits reachable from a specific branch, tag, or revision
  - `all_refs`: commits reachable from every ref in the repository
- Document kinds:
  - `commit`: normalized commit metadata and changed-path text
  - `log`: rendered `git log --stat` style text
- Pure `git` CLI backend, so there is no hard dependency on `pygit2`
- Convenience CLI with colored logs for ad hoc retrieval
- Default CLI behavior targets the current repo (`.`) and indexes all refs via `--ref all`

## Installation

```bash
pip install swarmauri_vectorstore_git
```

## Usage

```python
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_git import GitVectorStore

store = GitVectorStore(
    repo_path=".",
    scope="all_refs",
    document_kinds=("commit", "log"),
)

store.build_index()
results = store.retrieve("oauth token bug", top_k=3)

for document in results:
    print(document.metadata["oid"], document.metadata["kind"])
    print(document.content[:200])
```

## CLI

```bash
gitvs query --query "memory leak fix" --top-k 5
```

To inspect a specific retrieved document:

```bash
gitvs show --ref feature/my-branch --document-id <document-id>
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
