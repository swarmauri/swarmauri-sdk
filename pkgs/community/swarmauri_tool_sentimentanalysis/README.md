
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_sentimentanalysis/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_sentimentanalysis" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_tool_sentimentanalysis/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_sentimentanalysis/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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

