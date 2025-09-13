
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_dalechallreadability" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_dalechallreadability" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_dalechallreadability" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_dalechallreadability?label=swarmauri_tool_dalechallreadability&color=green" alt="PyPI - swarmauri_tool_dalechallreadability"/></a>
</p>

---

# Swarmauri Tool Dale-Chall Readability

A tool for calculating the Dale-Chall Readability Score using the textstat library.

## Installation

```bash
pip install swarmauri_tool_dalechallreadability
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.tools.DaleChallReadabilityTool import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()
input_data = {"input_text": "This is a simple sentence for testing purposes."}
result = tool(input_data)
print(result)  # Output: {'dale_chall_score': 7.98}
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
