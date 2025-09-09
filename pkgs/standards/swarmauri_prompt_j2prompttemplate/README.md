<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_j2prompttemplate/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_j2prompttemplate" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_prompt_j2prompttemplate.svg"/></a>
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
