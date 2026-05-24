![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_textlength/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_textlength/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_textlength" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_textlength?label=swarmauri_tool_textlength&color=green" alt="PyPI - swarmauri_tool_textlength"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Text Length

`swarmauri_tool_textlength` is a Swarmauri text-analysis tool that measures
characters, words, and sentences using NLTK tokenization. It is useful for
content QA, moderation gates, prompt-budget checks, readability workflows, and
agentic text analytics.

## Why Use Swarmauri Tool Text Length

- Measure content size with a Swarmauri-native tool interface.
- Track character, word, and sentence counts from a single call.
- Add length checks to moderation, documentation, or editorial pipelines.
- Reuse the same tool in agents, notebooks, scripts, and backend workflows.

## FAQ

> **What does the tool return?**  
> A dictionary with `num_characters`, `num_words`, and `num_sentences`.

> **Are spaces included in the character count?**  
> No. The current implementation excludes space characters.

> **What tokenizer does it use?**  
> It uses NLTK sentence and word tokenizers and downloads `punkt_tab` at import
> time if needed.

> **Is it English-specific?**  
> The default tokenization behavior is best suited to English text unless you
> swap in different tokenization logic.

## Features

- Swarmauri `ToolBase` implementation registered as `TextLengthTool`.
- Character, word, and sentence counts in one structured response.
- NLTK-based tokenization for more useful word and sentence splitting.
- Works well in content governance, prompt analytics, and editorial checks.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_textlength
```

```bash
pip install swarmauri_tool_textlength
```

## Usage

```python
from swarmauri_tool_textlength import TextLengthTool

tool = TextLengthTool()
metrics = tool("This is a simple test sentence.")

print(metrics)
```

## Examples

### Measure prompt length before model submission

```python
from swarmauri_tool_textlength import TextLengthTool

tool = TextLengthTool()
metrics = tool("Summarize the following release notes for an executive audience.")

print(metrics["num_words"])
```

### Check documentation size in a content pipeline

```python
from pathlib import Path
from swarmauri_tool_textlength import TextLengthTool

tool = TextLengthTool()

for path in Path("docs").rglob("*.md"):
    metrics = tool(path.read_text(encoding="utf-8"))
    print(path, metrics)
```

### Register the tool inside a Swarmauri tool registry

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_textlength import TextLengthTool

tools = ToolCollection(tools=[TextLengthTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_searchword](https://pypi.org/project/swarmauri_tool_searchword/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
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
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Pre-download `punkt_tab` for offline or containerized deployments.
- Treat counts as language-sensitive when processing non-English corpora.
- Pair text-length checks with readability tools when enforcing content style.
- If you need whitespace-inclusive counts, extend the character-count logic
  downstream.

## License

This project is licensed under the Apache-2.0 License.

