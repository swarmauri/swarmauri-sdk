![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_sentencecomplexity" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_sentencecomplexity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_sentencecomplexity" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_sentencecomplexity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_sentencecomplexity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_sentencecomplexity?label=swarmauri_tool_sentencecomplexity&color=green" alt="PyPI - swarmauri_tool_sentencecomplexity"/></a>
</p>

---

# Swarmauri Tool · Sentence Complexity

A Swarmauri NLP tool that evaluates sentence complexity by measuring average sentence length and estimating clause counts. Use it to monitor writing style, enforce readability requirements, or trigger editorial suggestions in agents.

- Tokenizes text with NLTK to compute sentence and word counts.
- Approximates clause density via punctuation and coordinating/subordinating conjunctions.
- Returns structured metrics suitable for analytics dashboards or conversational feedback.

## Requirements

- Python 3.10 – 3.13.
- `nltk` (downloads the `punkt_tab` tokenizer data on first import).
- Core Swarmauri dependencies (`swarmauri_base`, `swarmauri_standard`, `pydantic`).

## Installation

Choose the packaging workflow that matches your project; each command resolves the dependencies.

**pip**

```bash
pip install swarmauri_tool_sentencecomplexity
```

**Poetry**

```bash
poetry add swarmauri_tool_sentencecomplexity
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_sentencecomplexity

# or install into the active environment without modifying pyproject.toml
uv pip install swarmauri_tool_sentencecomplexity
```

> Tip: Pre-download the NLTK tokenizer resources in deployment images (`python -m nltk.downloader punkt_tab`) to avoid runtime network calls.

## Quick Start

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

text = "This is a simple sentence. This is another sentence, with a clause."

complexity_tool = SentenceComplexityTool()
result = complexity_tool(text)

print(result)
# {
#   'average_sentence_length': 7.5,
#   'average_clauses_per_sentence': 1.5
# }
```

The tool raises `ValueError` when the input text is empty or whitespace.

## Usage Scenarios

### Flag Long Sentences During Editing

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

complexity = SentenceComplexityTool()
article = Path("drafts/whitepaper.txt").read_text(encoding="utf-8")
metrics = complexity(article)

if metrics["average_sentence_length"] > 25:
    print("Consider splitting long sentences to improve readability.")
```

### Integrate With a Swarmauri Agent for Style Coaching

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

registry = ToolRegistry()
registry.register(SentenceComplexityTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="Analyze the complexity of: 'While the system scales, it may introduce latency delays.'")
response = agent.run(message)
print(response)
```

### Compare Versions of a Document Over Time

```python
from swarmauri_tool_sentencecomplexity import SentenceComplexityTool

complexity = SentenceComplexityTool()
versions = {
    "draft": open("draft.txt").read(),
    "final": open("final.txt").read(),
}

for label, text in versions.items():
    metrics = complexity(text)
    print(f"{label}: {metrics['average_sentence_length']:.1f} words, {metrics['average_clauses_per_sentence']:.2f} clauses")
```

Track whether edits are making the writing clearer or more complex.

## Troubleshooting

- **`LookupError: Resource punkt_tab not found`** – Run `python -m nltk.downloader punkt_tab` before executing the tool, especially in offline environments.
- **Low clause counts for technical prose** – The heuristic relies on commas/semicolons and common conjunctions; adjust or extend the tool if you need domain-specific parsing.
- **Non-English text** – Tokenization models are optimized for English. Supply language-appropriate tokenizers before using the tool for other languages.

## License

`swarmauri_tool_sentencecomplexity` is released under the Apache 2.0 License. See `LICENSE` for details.
