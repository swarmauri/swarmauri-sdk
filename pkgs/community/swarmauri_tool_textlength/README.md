
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_textlength" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_textlength" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_textlength" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_textlength?label=swarmauri_tool_textlength&color=green" alt="PyPI - swarmauri_tool_textlength"/></a>
</p>

---

# Swarmauri Tool Text Length

A Swarmauri tool that calculates the length of text in terms of characters, words, and sentences using NLTK tokenization.

## Installation

```bash
pip install swarmauri_tool_textlength
```

## Usage
Here's a simple example of how to use the TextLengthTool:

```python
from swarmauri.tools.TextLengthTool import TextLengthTool

# Initialize the tool
tool = TextLengthTool()

# Analyze text
text = "This is a simple test sentence."
result = tool(text)

# Access the results
print(f"Characters: {result['num_characters']}")  # 26
print(f"Words: {result['num_words']}")           # 7
print(f"Sentences: {result['num_sentences']}")   # 1
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

