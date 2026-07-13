![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://static.pepy.tech/badge/swarmauri_tool_queryknowledgebase/month)](https://pepy.tech/project/swarmauri_tool_queryknowledgebase)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_queryknowledgebase.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_queryknowledgebase/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tool_queryknowledgebase/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_queryknowledgebase)](https://pypi.org/project/swarmauri_tool_queryknowledgebase/)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_queryknowledgebase)](https://pypi.org/project/swarmauri_tool_queryknowledgebase/)

# Swarmauri Query Knowledge Base Tool

`swarmauri_tool_queryknowledgebase` exposes ranked knowledge-base retrieval as a Swarmauri tool while preserving document content, metadata, identifiers, and scores.

## Features

- Uses the repository-standard `retrieve(query, top_k)` workflow.
- Returns structured, ranked results instead of flattening documents into text.
- Supports exact-match metadata filtering and bounded result counts.
- Keeps runtime knowledge-base adapters out of serialized tool state.
- Wraps provider failures without leaking connection details.

## Installation

```bash
uv add swarmauri_tool_queryknowledgebase
```

```bash
pip install swarmauri_tool_queryknowledgebase
```

## Usage

```python
from swarmauri_tool_queryknowledgebase import QueryKnowledgeBaseTool

tool = QueryKnowledgeBaseTool(knowledge_base=my_document_store)
results = tool(
    "How are API keys rotated?",
    top_k=3,
    metadata_filter={"product": "sdk"},
)

for result in results:
    print(result["rank"], result["content"], result["metadata"])
```

The configured knowledge base must implement `retrieve(query, top_k=5)` and return documents or dictionaries in relevance order.

## Project Links

- [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk)
- [Contributing guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)

## License

Apache-2.0.
