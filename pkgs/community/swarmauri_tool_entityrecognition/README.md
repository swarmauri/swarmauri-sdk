
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

A Swarmauri tool that extracts named entities from text using a pre-trained NLP model.

## Installation

```bash
pip install swarmauri_tool_entityrecognition
```

## Usage

Here's a basic example of how to use the Entity Recognition Tool:

```python
from swarmauri.tools.EntityRecognitionTool import EntityRecognitionTool

# Initialize the tool
tool = EntityRecognitionTool()

# Example text for entity recognition
text = "Apple Inc. is an American multinational technology company."

# Get entities from the text
result = tool(text=text)

# The result will contain entities in JSON format
print(result["entities"])
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
