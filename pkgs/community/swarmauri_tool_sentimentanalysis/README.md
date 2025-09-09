
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

