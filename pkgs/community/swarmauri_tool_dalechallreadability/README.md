![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_dalechallreadability" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_dalechallreadability.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_dalechallreadability" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_dalechallreadability" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_dalechallreadability/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_dalechallreadability?label=swarmauri_tool_dalechallreadability&color=green" alt="PyPI - swarmauri_tool_dalechallreadability"/></a>
</p>

---

# Swarmauri Tool Dale-Chall Readability

Tool wrapper around [`textstat`](https://pypi.org/project/textstat/) to compute the Dale–Chall readability score for a block of text via the Swarmauri tool interface.

## Features

- Accepts an `input_text` parameter and returns `{"dale_chall_score": <float>}`.
- Uses `textstat.dale_chall_readability_score` under the hood.
- Input validation ensures the required parameter is present before calculation.

## Prerequisites

- Python 3.10 or newer.
- `textstat` and `pyphen` dictionaries (installed automatically). Some textstat metrics may download additional word lists on first use.

## Installation

```bash
# pip
pip install swarmauri_tool_dalechallreadability

# poetry
poetry add swarmauri_tool_dalechallreadability

# uv (pyproject-based projects)
uv add swarmauri_tool_dalechallreadability
```

## Quickstart

```python
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

text = "This is a simple sentence for testing purposes."
tool = DaleChallReadabilityTool()
result = tool({"input_text": text})
print(result)
```

## Usage in Tool Chains

```python
from swarmauri_tool_dalechallreadability import DaleChallReadabilityTool

def grade_paragraph(paragraph: str) -> float:
    tool = DaleChallReadabilityTool()
    score = tool({"input_text": paragraph})["dale_chall_score"]
    return score
```

## Tips

- Dale–Chall scores roughly map to U.S. grade levels; lower scores indicate easier reading.
- Pre-clean text (remove markup, normalize whitespace) for consistent scoring.
- Combine with Swarmauri measurements or parsers to evaluate readability across multiple documents.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
