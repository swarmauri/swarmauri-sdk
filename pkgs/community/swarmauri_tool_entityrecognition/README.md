![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_entityrecognition/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_entityrecognition/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_entityrecognition" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_entityrecognition?label=swarmauri_tool_entityrecognition&color=green" alt="PyPI - swarmauri_tool_entityrecognition"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Entity Recognition

`swarmauri_tool_entityrecognition` is the Swarmauri named-entity recognition
tool built on Hugging Face transformers. It wraps the `pipeline("ner")`
inference surface and returns a JSON-encoded dictionary of detected entity
tokens grouped by entity label.

## Why Use Swarmauri Tool Entity Recognition

- Add transformer-based entity extraction to tool-calling or agent workflows.
- Return a simple serialized entity payload that can be passed across tool
  boundaries without introducing custom object types.
- Use Hugging Face token-classification models when you want a hosted-model-like
  NER interface in local Python workflows.
- Combine entity extraction with other Swarmauri tools for routing,
  classification, or post-processing pipelines.

## FAQ

> **What does this tool return?**  
> A dictionary with one key, `entities`, whose value is a JSON string
> containing grouped entity tokens.

> **What model does it use?**  
> The current implementation calls `pipeline("ner")`, so the default model is
> whichever Hugging Face pipeline resolves for local environment defaults.

> **Does it return full entity spans?**  
> Not directly. It groups model output tokens by label. Downstream consumers may
> need to reconstruct phrase spans.

> **Does it download weights on first use?**  
> Yes. Hugging Face model assets are downloaded on first execution if they are
> not already cached.

## Features

- Hugging Face transformer-based named-entity recognition.
- Swarmauri `ToolBase` integration for direct tool invocation.
- JSON-encoded entity grouping keyed by model labels such as `B-ORG`, `I-ORG`,
  `B-PER`, `B-LOC`, or similar.
- Suitable for LLM tool-calling, preprocessing, and extraction workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_entityrecognition
```

```bash
pip install swarmauri_tool_entityrecognition
```

## Usage

```python
import json
from swarmauri_tool_entityrecognition import EntityRecognitionTool

tool = EntityRecognitionTool()
result = tool(text="Apple Inc. is an American multinational technology company.")
entities = json.loads(result["entities"])
print(entities)
```

## Examples

### Extract labeled entity tokens

```python
import json
from swarmauri_tool_entityrecognition import EntityRecognitionTool

tool = EntityRecognitionTool()
result = tool(text="Tim Cook spoke in New York on behalf of Apple Inc.")

print(json.loads(result["entities"]))
```

### Pass tool output into downstream processing

```python
import json
from swarmauri_tool_entityrecognition import EntityRecognitionTool

tool = EntityRecognitionTool()
payload = tool(text="Microsoft opened a new office in London.")
grouped = json.loads(payload["entities"])

for label, tokens in grouped.items():
    print(label, tokens)
```

## Related Packages

- [swarmauri_parser_entityrecognition](https://pypi.org/project/swarmauri_parser_entityrecognition/)
- [swarmauri_tool_sentimentanalysis](https://pypi.org/project/swarmauri_tool_sentimentanalysis/)
- [swarmauri_parser_textblob](https://pypi.org/project/swarmauri_parser_textblob/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Hugging Face token classification task guide](https://huggingface.co/docs/transformers/tasks/token_classification)
- [Transformers pipeline documentation](https://huggingface.co/docs/transformers/main_classes/pipelines)

## Best Practices

- Cache Hugging Face assets in CI or deployment environments to avoid repeated
  downloads.
- Reconstruct contiguous entity spans if your application needs phrase-level
  entities instead of grouped tokens.
- Pin or subclass with a specific NER model if you need deterministic behavior
  across environments.
- Treat the returned JSON string as a transport format and normalize it before
  indexing or analytics.

## License

This project is licensed under the Apache-2.0 License.


