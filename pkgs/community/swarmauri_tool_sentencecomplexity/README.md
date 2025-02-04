![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_sentencecomplexity)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_sentencecomplexity)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_sentencecomplexity)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_sentencecomplexity?label=swarmauri_tool_sentencecomplexity&color=green)

</div>

---

# Sentence Complexity Tool

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