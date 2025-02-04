![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_dalechallreadability)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_dalechallreadability)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_dalechallreadability)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_dalechallreadability?label=swarmauri_tool_dalechallreadability&color=green)

</div>

---

# Swarmauri Tool Dale-Chall Readability

A tool for calculating the Dale-Chall Readability Score using the textstat library.

## Installation

```bash
pip install swarmauri_tool_dalechallreadability
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.tools.DaleChallReadabilityTool import DaleChallReadabilityTool

tool = DaleChallReadabilityTool()
input_data = {"input_text": "This is a simple sentence for testing purposes."}
result = tool(input_data)
print(result)  # Output: {'dale_chall_score': 7.98}
```
## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
