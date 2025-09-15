
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_sentencecomplexity" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_sentencecomplexity" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_sentencecomplexity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_sentencecomplexity?label=swarmauri_tool_sentencecomplexity&color=green" alt="PyPI - swarmauri_tool_sentencecomplexity"/></a>
</p>

---

# Swarmauri Tool Sentencecomplexity

A tool for evaluating sentence complexity based on average sentence length and the number of clauses.

## Installation

```bash
pip install swarmauri_tool_sentencecomplexity
```

## Usage
The SentenceComplexityTool analyzes text and returns metrics about sentence complexity.

```python
from swarmauri.tools.sentencecomplexity import SentenceComplexityTool

# Initialize the tool
tool = SentenceComplexityTool()

# Analyze text
text = "This is a simple sentence. This is another sentence, with a clause."
result = tool(text)

print(result)
# Output: {
#     'average_sentence_length': 7.5,
#     'average_clauses_per_sentence': 1.5
# }
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
