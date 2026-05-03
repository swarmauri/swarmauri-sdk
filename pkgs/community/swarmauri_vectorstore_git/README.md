![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_vectorstore_git/">
        <img src="https://static.pepy.tech/badge/swarmauri_vectorstore_git/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_git/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_vectorstore_git.svg"/></a>
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

To inspect both document kinds together and return machine-readable output:

```bash
gitvs --ref HEAD --document-kind commit --document-kind log query --query "mojibake plugin readme" --top-k 2 --json
```

Actual output captured against the `swarmauri-sdk` repository:

```json
[
  {
    "id": "5fb843d09edc2be4e681d4cff73b11a677439588:commit",
    "metadata": {
      "oid": "5fb843d09edc2be4e681d4cff73b11a677439588",
      "kind": "commit",
      "scope": "head",
      "ref": null,
      "parents": [
        "0d29234100fd8bff6ace454cb5ede16d43550f20"
      ],
      "changed_paths": [
        "pkgs/plugins/EmbedXMP/README.md",
        "pkgs/plugins/example_plugin/README.md"
      ],
      "subject": "Fix mojibake in plugin README feature bullets",
      "author": {
        "name": "cobycloud",
        "email": "25079070+cobycloud@users.noreply.github.com",
        "time": "2026-05-03T01:51:22-05:00"
      },
      "committer": {
        "name": "cobycloud",
        "email": "25079070+cobycloud@users.noreply.github.com",
        "time": "2026-05-03T01:52:36-05:00"
      }
    },
    "content": "commit 5fb843d09edc2be4e681d4cff73b11a677439588\nscope head\nref HEAD\nsubject Fix mojibake in plugin README feature bullets\nauthor cobycloud <25079070+cobycloud@users.noreply.github.com>\ncommitter cobycloud <25079070+cobycloud@users.noreply.github.com>\nauthored_at 2026-05-03T01:51:22-05:00\ncommitted_at 2026-05-03T01:52:36-05:00\nparents 0d29234100fd8bff6ace454cb5ede16d43550f20\n\nmessage\nFix mojibake in plugin README feature bullets\n\nchanged_paths\npkgs/plugins/EmbedXMP/README.md\npkgs/plugins/example_plugin/README.md\n\ndiff_stats\npkgs/plugins/EmbedXMP/README.md       | 10 +++++-----\n pkgs/plugins/example_plugin/README.md |  8 ++++----\n 2 files changed, 9 insertions(+), 9 deletions(-)"
  },
  {
    "id": "5fb843d09edc2be4e681d4cff73b11a677439588:log",
    "metadata": {
      "oid": "5fb843d09edc2be4e681d4cff73b11a677439588",
      "kind": "log",
      "scope": "head",
      "ref": null,
      "subject": "Fix mojibake in plugin README feature bullets"
    },
    "content": "commit 5fb843d09edc2be4e681d4cff73b11a677439588\nAuthor:     cobycloud <25079070+cobycloud@users.noreply.github.com>\nAuthorDate: 2026-05-03T01:51:22-05:00\nCommit:     cobycloud <25079070+cobycloud@users.noreply.github.com>\nCommitDate: 2026-05-03T01:52:36-05:00\n\n    Fix mojibake in plugin README feature bullets\n\n pkgs/plugins/EmbedXMP/README.md       | 10 +++++-----\n pkgs/plugins/example_plugin/README.md |  8 ++++----\n 2 files changed, 9 insertions(+), 9 deletions(-)"
  }
]
```

To inspect a specific retrieved document:

```bash
gitvs --ref HEAD show --document-id 5fb843d09edc2be4e681d4cff73b11a677439588:commit
```

Actual output:

```text
commit 5fb843d09edc2be4e681d4cff73b11a677439588
scope head
ref HEAD
subject Fix mojibake in plugin README feature bullets
author cobycloud <25079070+cobycloud@users.noreply.github.com>
committer cobycloud <25079070+cobycloud@users.noreply.github.com>
authored_at 2026-05-03T01:51:22-05:00
committed_at 2026-05-03T01:52:36-05:00
parents 0d29234100fd8bff6ace454cb5ede16d43550f20

message
Fix mojibake in plugin README feature bullets

changed_paths
pkgs/plugins/EmbedXMP/README.md
pkgs/plugins/example_plugin/README.md

diff_stats
pkgs/plugins/EmbedXMP/README.md       | 10 +++++-----
 pkgs/plugins/example_plugin/README.md |  8 ++++----
 2 files changed, 9 insertions(+), 9 deletions(-)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
