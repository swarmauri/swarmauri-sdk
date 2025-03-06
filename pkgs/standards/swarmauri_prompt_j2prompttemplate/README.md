![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_j2prompttemplate" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tool_j2prompttemplate/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_tool_j2prompttemplate/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_j2prompttemplate" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_j2prompttemplate" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_j2prompttemplate?label=swarmauri_tool_j2prompttemplate&color=green" alt="PyPI - swarmauri_tool_j2prompttemplate"/></a>
</p>

---

# Swarmauri Tool J2PromptTemplate

A Swarmauri package that provides tools for generating prompts using Jinja2 templates. Includes support for dynamic template rendering and variable substitution.

## Installation

```bash
pip install swarmauri_tool_j2prompttemplate
```

## Usage

### Basic Template Rendering
```python
from swarmauri_tool_j2prompttemplate.J2PromptTemplate import J2PromptTemplate

# Create a template instance
template = J2PromptTemplate(template="Hello, {{ name }}!")

# Generate a prompt
result = template(variables={"name": "World"})
print(result)  # Output: Hello, World!
```

### Template Rendering from File
```python
from swarmauri_tool_j2prompttemplate.J2PromptTemplate import J2PromptTemplate
from pathlib import Path

# Create a template instance with a file path
template_path = Path("path/to/template.j2")
template = J2PromptTemplate(template=template_path)

# Generate a prompt
result = template(variables={"name": "World"})
print(result)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
