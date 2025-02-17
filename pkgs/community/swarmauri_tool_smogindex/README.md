![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_tool_smogindex)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_tool_smogindex)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_tool_smogindex)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_tool_smogindex?label=swarmauri_tool_smogindex&color=green)

</div>

---

# SMOG Index Tool

A tool for calculating the SMOG (Simple Measure of Gobbledygook) Index of text, which estimates the years of education needed to understand a piece of written material.

## Installation

```bash
pip install swarmauri_tool_smogindex
```

## Usage

```python
from swarmauri.tools.SMOGIndexTool import SMOGIndexTool

# Initialize the tool
tool = SMOGIndexTool()

# Analyze text
text = "This is a sample text with some complex sentences and polysyllabic words to test the SMOG Index calculation."
result = tool(text)

# Get the SMOG index
smog_index = result['smog_index']
print(f"SMOG Index: {smog_index}")  # Output: SMOG Index: 8.5
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

