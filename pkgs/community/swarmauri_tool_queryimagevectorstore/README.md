![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![Downloads](https://static.pepy.tech/badge/swarmauri_tool_queryimagevectorstore/month)](https://pepy.tech/project/swarmauri_tool_queryimagevectorstore)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_queryimagevectorstore.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_queryimagevectorstore/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tool_queryimagevectorstore/)
[![License](https://img.shields.io/pypi/l/swarmauri_tool_queryimagevectorstore)](https://pypi.org/project/swarmauri_tool_queryimagevectorstore/)
[![Release](https://img.shields.io/pypi/v/swarmauri_tool_queryimagevectorstore)](https://pypi.org/project/swarmauri_tool_queryimagevectorstore/)

# Swarmauri Query Image Vector Store Tool

`swarmauri_tool_queryimagevectorstore` queries image-vector indexes with either an image input or a precomputed numeric embedding and returns structured ranked matches.

## Features

- Accepts exactly one image or embedding per query.
- Converts images through an explicit `infer_vector(image)` adapter.
- Supports `retrieve_by_vector` and `similarity_search_by_vector` stores.
- Preserves identifiers, scores, content, URIs, and metadata.
- Applies exact-match metadata filters and bounded result counts.

## Installation

```bash
uv add swarmauri_tool_queryimagevectorstore
```

```bash
pip install swarmauri_tool_queryimagevectorstore
```

## Usage

```python
from swarmauri_tool_queryimagevectorstore import QueryImageVectorStoreTool

tool = QueryImageVectorStoreTool(
    vector_store=my_image_index,
    image_embedder=my_vision_embedder,
)

matches = tool(
    image=image_payload,
    top_k=5,
    metadata_filter={"category": "diagram"},
)
```

For precomputed embeddings, call `tool(embedding=[...], top_k=5)`. The vector store must expose `retrieve_by_vector(embedding, top_k=...)` or `similarity_search_by_vector(embedding, top_k=...)`.

## Project Links

- [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk)
- [Contributing guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)

## License

Apache-2.0.
