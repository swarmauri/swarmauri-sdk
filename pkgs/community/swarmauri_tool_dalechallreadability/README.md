
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_dalechallreadability" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_dalechallreadability/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_dalechallreadability/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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
