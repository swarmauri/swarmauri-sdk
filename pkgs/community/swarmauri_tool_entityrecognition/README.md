![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_entityrecognition" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_entityrecognition.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_entityrecognition" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_entityrecognition" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_entityrecognition/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_entityrecognition?label=swarmauri_tool_entityrecognition&color=green" alt="PyPI - swarmauri_tool_entityrecognition"/></a>
</p>

---

# Swarmauri Tool Entity Recognition

Named-entity recognition tool for Swarmauri based on Hugging Face transformers. Uses the default `pipeline("ner")` model to detect tokens labeled as PERSON, ORG, LOC, etc., and returns a JSON-encoded dictionary of entities grouped by label.

## Features

- Wraps the transformers NER pipeline in a Swarmauri `ToolBase` component.
- Auto-downloads the default model on first run (usually `dslim/bert-base-NER`).
- Aggregates entity tokens by label and returns them as a JSON string in the `entities` key.

## Prerequisites

- Python 3.10 or newer.
- `transformers`, `torch`, and associated dependencies (installed automatically). Ensure GPU/CPU compatibility for PyTorch according to your environment.
- Internet access on first run to download model weights.

## Installation

```bash
# pip
pip install swarmauri_tool_entityrecognition

# poetry
poetry add swarmauri_tool_entityrecognition

# uv (pyproject-based projects)
uv add swarmauri_tool_entityrecognition
```

## Quickstart

```python
import json
from swarmauri_tool_entityrecognition import EntityRecognitionTool

text = "Apple Inc. is an American multinational technology company."
tool = EntityRecognitionTool()
result = tool(text=text)

entities = json.loads(result["entities"])
print(entities)
```

Example output:
```
{"B-ORG": ["Apple", "Inc."], "B-MISC": ["American"], "I-MISC": ["multinational"], ...}
```

## Tips

- The default pipeline tokenizes into subwords; reconstruct phrases by joining consecutive tokens with the same label when needed.
- Specify a different model by subclassing and passing `pipeline("ner", model="<model>")` if you require language-specific NER.
- Cache Hugging Face models (`HF_HOME`) in CI or container builds to avoid repeated downloads.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
