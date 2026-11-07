![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_addcontenttorag/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_addcontenttorag" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_addcontenttorag/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_addcontenttorag.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_addcontenttorag/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_addcontenttorag" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_addcontenttorag/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_addcontenttorag" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_addcontenttorag/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_addcontenttorag?label=swarmauri_tool_addcontenttorag&color=green" alt="PyPI - swarmauri_tool_addcontenttorag"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Add Content to RAG Tool

`swarmauri_tool_addcontenttorag` writes text into a RAG knowledge base, with
optional metadata tags. It is the storage counterpart of
`swarmauri_tool_queryknowledgebase`: one tool puts content in, the other reads
ranked results back out.

## Features

- **Add text content** to any knowledge base that provides
  `add_documents(documents)`, the same contract the query tool reads from.
- **Attach metadata tags** to each write, so results can be filtered later.
- **Copies the caller's mapping** instead of storing their dict, so a later
  mutation elsewhere cannot rewrite what was indexed.
- **Keeps the adapter out of serialized state.** The knowledge base is excluded
  from `model_dump()`, so a tool can be logged or persisted without carrying a
  live database handle.
- **Wraps store failures** in a `RuntimeError` without passing connection
  details through to the caller.

## Installation

```bash
# With uv
uv add swarmauri_tool_addcontenttorag

# With pip
pip install swarmauri_tool_addcontenttorag
```

## Usage

```python
from swarmauri_tool_addcontenttorag import AddContentToRAGTool


class InMemoryKnowledgeBase:
    """Any object with add_documents(documents) works."""

    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)


knowledge_base = InMemoryKnowledgeBase()

tool = AddContentToRAGTool()
tool.knowledge_base = knowledge_base

tool(content="Reset your password from Settings.", metadata={"source": "handbook"})
# {"added": 1, "content_length": 34, "metadata": {"source": "handbook"}}

knowledge_base.documents
# [{"content": "Reset your password from Settings.",
#   "metadata": {"source": "handbook"}}]
```

### Result keys

| Key | Type | Meaning |
| --- | --- | --- |
| `added` | `int` | Number of documents written |
| `content_length` | `int` | Characters written |
| `metadata` | `dict` | Tags stored with the content |

## Expected workflows

- **Load a knowledge base at startup.** Add each document or chunk before the
  agent starts answering.
- **Update it while running.** Add new content as it arrives; the paired query
  tool sees it without a restart.
- **Tag as you write.** Store `source`, `page` or `version` with each entry so
  retrieval can filter on it.

## FAQ

> **Does it chunk content?**  
> No. It writes what it is given. Chunking belongs upstream, where the
> document is split, so the tool never silently alters what was stored.

> **How is versioning handled?**  
> Through metadata. Tag each write with a version or timestamp; replacing an
> earlier version is the store's decision, not this tool's.

> **What if the store fails mid-write?**  
> The error is wrapped in a `RuntimeError` with the original chained for logs
> but not shown to the caller.


## Metadata ownership and ingestion scope

Mapping inputs, including read-only mappings, are normalized to a dict.
JSON-style metadata (nested built-in dictionaries, lists, and scalar values)
is deep-copied before creating the SDK `Document`. Returned metadata is a
separate snapshot of the submitted tags, so mutating these ordinary input or
returned containers cannot change stored document tags. Custom Python values
obey their own `deepcopy` protocol; objects that deliberately return themselves
from that protocol do not carry the same isolation guarantee. Both snapshots
are prepared before calling the store, so copy failures cannot report an error
after a successful write. Metadata must be a mapping whose values support
copying. Invalid input raises `ValueError` before any write.

This tool ingests one text document per call. Callers own format conversion,
chunking, preprocessing, and version conventions in metadata. The configured
store owns indexing, persistence, and replacement policy. The tool does not
claim automatic preprocessing or version management. Store failures expose a
generic public message; the chained original exception remains available to
trusted diagnostic code.
