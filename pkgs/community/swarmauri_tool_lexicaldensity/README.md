
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_lexicaldensity" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_lexicaldensity/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_lexicaldensity/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_lexicaldensity" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_lexicaldensity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_lexicaldensity?label=swarmauri_tool_lexicaldensity&color=green" alt="PyPI - swarmauri_tool_lexicaldensity"/></a>
</p>

---

# Swarmauri Tool Lexical Density

A tool for calculating the lexical density of text, indicating the proportion of content words (nouns, verbs, adjectives, and adverbs) relative to the total number of words.

## Installation

```bash
pip install swarmauri_tool_lexicaldensity
```

## Usage
```python
from swarmauri.tools.LexicalDensityTool import LexicalDensityTool

# Initialize the tool
tool = LexicalDensityTool()

# Calculate lexical density
text = "This is a test sentence."
result = tool(text)
print(result)  # Returns: {'lexical_density': <score>}
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
