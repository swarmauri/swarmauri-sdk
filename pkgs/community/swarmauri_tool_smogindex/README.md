![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_smogindex/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_smogindex/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_smogindex/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_smogindex.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_smogindex/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_smogindex/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_smogindex" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_smogindex/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_smogindex?label=swarmauri_tool_smogindex&color=green" alt="PyPI - swarmauri_tool_smogindex"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool SMOG Index

`swarmauri_tool_smogindex` is a Swarmauri readability tool for calculating the
SMOG Index, a well-known estimate of the education level needed to understand a
piece of writing. It is useful for compliance content, educational materials,
technical documentation, public-facing copy, and agent workflows that need a
quick readability score.

## Why Use Swarmauri Tool SMOG Index

- Estimate how difficult a text may be for readers to understand.
- Review whether copy meets documentation or policy readability targets.
- Add grade-level signals to editorial, education, or governance workflows.
- Compare document revisions with a consistent, interpretable metric.

## FAQ

> **What does the tool return?**  
> A dictionary with one key: `smog_index`.

> **How is the score estimated?**  
> The implementation counts sentences and polysyllabic words, then applies the
> standard SMOG formula.

> **What happens for empty text?**  
> The score returns `0.0` when no sentences are found.

> **Is this a full readability suite?**  
> No. It focuses specifically on the SMOG Index.

## Features

- Swarmauri `ToolBase` implementation registered as `SMOGIndexTool`.
- Calculates SMOG readability scores from raw text.
- Uses sentence tokenization plus polysyllable counting.
- Useful for document QA, public-language review, and education use cases.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_smogindex
```

```bash
pip install swarmauri_tool_smogindex
```

## Usage

```python
from swarmauri_tool_smogindex import SMOGIndexTool

tool = SMOGIndexTool()
result = tool("This is a sample text with complex sentences and polysyllabic words.")

print(result["smog_index"])
```

## Examples

### Score a policy document excerpt

```python
from swarmauri_tool_smogindex import SMOGIndexTool

tool = SMOGIndexTool()
score = tool("Authentication requirements shall be enforced through administrative verification procedures.")

print(score)
```

### Compare simplified and technical versions

```python
from swarmauri_tool_smogindex import SMOGIndexTool

tool = SMOGIndexTool()

simple = "Read the guide and follow the steps."
technical = "Operational remediation requires synchronized configuration validation across administrative boundaries."

print("simple", tool(simple))
print("technical", tool(technical))
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_smogindex import SMOGIndexTool

tools = ToolCollection(tools=[SMOGIndexTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_dalechallreadability](https://pypi.org/project/swarmauri_tool_dalechallreadability/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [SMOG formula overview](https://en.wikipedia.org/wiki/SMOG)
- [NLTK documentation](https://www.nltk.org/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Use the score comparatively across similar kinds of content.
- Expect very short texts to produce less stable readability estimates.
- Pre-download tokenizer resources in offline deployments.
- Pair SMOG with other readability and structure metrics for better judgment.

## License

This project is licensed under the Apache-2.0 License.
