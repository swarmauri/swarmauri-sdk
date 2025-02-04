![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_textlength)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_textlength)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_textlength)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_textlength?label=swarmauri_tool_textlength&color=green)

</div>

---

# Text Length Tool

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

