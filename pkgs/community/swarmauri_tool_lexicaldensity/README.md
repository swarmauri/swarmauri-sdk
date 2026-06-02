![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_lexicaldensity/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_lexicaldensity/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_lexicaldensity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_lexicaldensity?label=swarmauri_tool_lexicaldensity&color=green" alt="PyPI - swarmauri_tool_lexicaldensity"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Lexical Density

`swarmauri_tool_lexicaldensity` is a Swarmauri NLP tool for estimating lexical
density, the ratio of content words to total word count. It helps quantify how
information-dense a passage is, which makes it useful for readability reviews,
editorial QA, prompt analysis, educational tools, and agent-based writing
assistance.

## Why Use Swarmauri Tool Lexical Density

- Measure how content-heavy or function-word-heavy a text is.
- Compare drafts, prompts, or knowledge articles with a simple numeric signal.
- Feed lexical-density metrics into Swarmauri quality or moderation workflows.
- Pair lexical density with readability metrics for more complete text review.

## FAQ

> **What does lexical density measure?**  
> It estimates the percentage of content words such as nouns, verbs,
> adjectives, and adverbs relative to all words in the text.

> **What does the tool return?**  
> A dictionary with one key: `lexical_density`.

> **Does it rely on NLTK models?**  
> Yes. It uses NLTK tokenization and POS tagging resources.

> **Is it best suited for English text?**  
> Yes. The current POS-tagging setup is English-oriented.

## Features

- Swarmauri `ToolBase` implementation registered as `LexicalDensityTool`.
- Computes lexical density as a percentage value.
- Uses NLTK POS tagging to isolate content words.
- Useful for editorial, educational, prompt, and corpus-analysis workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_lexicaldensity
```

```bash
pip install swarmauri_tool_lexicaldensity
```

## Usage

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
result = tool("This report summarizes quarterly revenue growth across segments.")

print(result["lexical_density"])
```

## Examples

### Compare lexical density across drafts

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()

for label, text in {
    "draft": "We made a thing and it does stuff for users.",
    "final": "The platform automates retrieval, classification, and policy enforcement.",
}.items():
    print(label, tool(text))
```

### Score a prompt before sending it to an LLM

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
metrics = tool("Summarize operational risks, mitigation plans, and release dependencies.")

print(metrics)
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tools = ToolCollection(tools=[LexicalDensityTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)
- [swarmauri_tool_dalechallreadability](https://pypi.org/project/swarmauri_tool_dalechallreadability/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [NLTK documentation](https://www.nltk.org/)
- [textstat documentation](https://github.com/textstat/textstat)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Pre-download NLTK models in offline or containerized deployments.
- Compare lexical-density values across similar content types, not unrelated
  genres.
- Use lexical density alongside readability scores rather than as a sole
  quality metric.
- Expect shorter texts to produce noisier percentages.

## License

This project is licensed under the Apache-2.0 License.
