![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_lexicaldensity" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_lexicaldensity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_lexicaldensity" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_lexicaldensity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_lexicaldensity?label=swarmauri_tool_lexicaldensity&color=green" alt="PyPI - swarmauri_tool_lexicaldensity"/></a>
</p>

---

# Swarmauri Tool · Lexical Density

A Swarmauri-compatible NLP utility that measures the lexical density of text—the ratio of content words (nouns, verbs, adjectives, adverbs) versus the total token count. Use it to monitor writing complexity, automate readability checks, or surface style signals inside agent conversations.

- Tokenizes input with NLTK and tags parts of speech to isolate lexical items.
- Returns a percentage score so changes in density are easy to compare between drafts.
- Ships as a Swarmauri tool, ready for registration inside agents or pipelines.

## Requirements

- Python 3.10 – 3.13.
- `nltk` with the `punkt_tab` and `averaged_perceptron_tagger_eng` resources available (downloaded at runtime).
- `textstat` for robust lexicon counting.
- Core dependencies (`swarmauri_base`, `swarmauri_standard`, `pydantic`).

## Installation

Pick the installer that matches your project; each command resolves the transitive requirements.

**pip**

```bash
pip install swarmauri_tool_lexicaldensity
```

**Poetry**

```bash
poetry add swarmauri_tool_lexicaldensity
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_lexicaldensity

# or install into the running environment without touching pyproject.toml
uv pip install swarmauri_tool_lexicaldensity
```

> Tip: If you deploy in an offline environment, download the required NLTK models during build time (`python -m nltk.downloader punkt_tab averaged_perceptron_tagger_eng`).

## Quick Start

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

text = "This report summarizes quarterly revenue growth across all segments."

lexical_density_tool = LexicalDensityTool()
result = lexical_density_tool(text)

print(result)
# {'lexical_density': 58.333333333333336}
```

The tool returns a floating-point percentage. Use the same instance to score multiple passages.

## Usage Scenarios

### Enforce Style Guidelines in Content Pipelines

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

product_copy = "Introducing our new AI-powered workstation with modular expansion."

checker = LexicalDensityTool()
score = checker(product_copy)["lexical_density"]

if score < 40:
    raise ValueError(f"Copy too simple (density={score:.1f}%). Add more substantive language.")
```

Gate marketing copy or documentation PRs based on desired complexity thresholds.

### Analyze Conversations in a Swarmauri Agent

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_lexicaldensity import LexicalDensityTool

registry = ToolRegistry()
registry.register(LexicalDensityTool())
agent = Agent(tool_registry=registry)

utterance = "Could you elaborate on the architectural trade-offs in the data plane?"
result = agent.tools["LexicalDensityTool"](utterance)
print(result)
```

Use lexical density as a signal to adjust agent tone or escalate queries to human operators.

### Batch Score Documents and Track Trends

```python
from pathlib import Path
from swarmauri_tool_lexicaldensity import LexicalDensityTool

lexical_density = LexicalDensityTool()
corpus_dir = Path("reports/")

scores = []
for doc in corpus_dir.glob("*.txt"):
    text = doc.read_text(encoding="utf-8")
    scores.append((doc.name, lexical_density(text)["lexical_density"]))

for name, score in sorted(scores, key=lambda item: item[1], reverse=True):
    print(f"{name}: {score:.2f}% lexical words")
```

Monitor writing complexity across a corpus of articles or support responses.

## Troubleshooting

- **`LookupError` for NLTK resources** – Ensure `punkt_tab` and `averaged_perceptron_tagger_eng` are downloaded prior to calling the tool (see `nltk.download(...)`).
- **Low density on short texts** – Very short messages yield coarse percentages. Aggregate multiple utterances or relax thresholds for brief content.
- **Non-English text** – POS tagging models target English. Swap in language-specific models before using the tool with multilingual corpora.

## License

`swarmauri_tool_lexicaldensity` is released under the Apache 2.0 License. See `LICENSE` for full details.
