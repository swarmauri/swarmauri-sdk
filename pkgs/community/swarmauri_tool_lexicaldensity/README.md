![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_lexicaldensity)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_lexicaldensity)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_lexicaldensity)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_lexicaldensity?label=swarmauri_tool_lexicaldensity&color=green)

</div>

---

# Lexical Density Tool

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
