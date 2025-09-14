
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_sentimentanalysis" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentimentanalysis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentimentanalysis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_sentimentanalysis" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_sentimentanalysis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_sentimentanalysis?label=swarmauri_tool_sentimentanalysis&color=green" alt="PyPI - swarmauri_tool_sentimentanalysis"/></a>
</p>

---

# Swarmauri Tool Sentimentanalysis

A tool for analyzing the sentiment of text using Hugging Face's transformers library. This tool provides simple sentiment analysis capabilities, classifying text as POSITIVE, NEGATIVE, or NEUTRAL.

## Installation

```bash
pip install swarmauri_tool_sentimentanalysis
```

## Usage
Here's a basic example of how to use the Sentiment Analysis Tool:
```python
from swarmauri.tools.SentimentAnalysisTool import SentimentAnalysisTool

# Initialize the tool
tool = SentimentAnalysisTool()

# Analyze sentiment
result = tool("I love this product!")
print(result)  # {'sentiment': 'POSITIVE'}

# Another example
result = tool("This product is okay.")
print(result)  # {'sentiment': 'NEUTRAL'}
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

