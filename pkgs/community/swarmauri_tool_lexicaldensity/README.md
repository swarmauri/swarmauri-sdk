
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_lexicaldensity" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity.svg"/></a>
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
