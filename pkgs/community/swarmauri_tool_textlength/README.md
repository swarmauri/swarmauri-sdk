![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_textlength" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_textlength.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_textlength" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_textlength" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_textlength/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_textlength?label=swarmauri_tool_textlength&color=green" alt="PyPI - swarmauri_tool_textlength"/></a>
</p>

---

# Swarmauri Tool · Text Length

A Swarmauri-ready helper that measures text length in characters, words, and sentences using NLTK tokenization. Drop it into content pipelines, moderation bots, or editorial agents to monitor message size and cadence.

- Counts characters (excluding spaces) for quick size checks.
- Uses NLTK tokenizers to calculate word and sentence totals accurately.
- Returns a structured dictionary suitable for logging, analytics, or conversational outputs.

## Requirements

- Python 3.10 – 3.13.
- `nltk` with the `punkt_tab` resource available (downloaded automatically on import).
- Core Swarmauri dependencies (`swarmauri_base`, `swarmauri_standard`, `pydantic`).

## Installation

Pick the packaging tool that fits your workflow; each command installs dependencies.

**pip**

```bash
pip install swarmauri_tool_textlength
```

**Poetry**

```bash
poetry add swarmauri_tool_textlength
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_textlength

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_textlength
```

> Tip: When building containers or offline environments, pre-fetch NLTK data with `python -m nltk.downloader punkt_tab` to avoid runtime downloads.

## Quick Start

```python
from swarmauri_tool_textlength import TextLengthTool

text = "This is a simple test sentence."

length_tool = TextLengthTool()
result = length_tool(text)

print(result)
# {
#   'num_characters': 26,
#   'num_words': 7,
#   'num_sentences': 1
# }
```

## Usage Scenarios

### Enforce Message Length in Moderation Bots

```python
from swarmauri_tool_textlength import TextLengthTool

length_checker = TextLengthTool()
message = """Please keep replies under 50 words so the queue stays manageable."""

metrics = length_checker(message)
if metrics["num_words"] > 50:
    raise ValueError("Message too long for moderation queue")
```

### Provide Real-Time Feedback in a Swarmauri Agent

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_textlength import TextLengthTool

registry = ToolRegistry()
registry.register(TextLengthTool())
agent = Agent(tool_registry=registry)

message = HumanMessage(content="Analyze how long this paragraph is compared to our guideline.")
response = agent.run(message)
print(response)
```

### Batch Audit Documentation for Sentence Length

```python
from pathlib import Path
from swarmauri_tool_textlength import TextLengthTool

length_tool = TextLengthTool()

for doc in Path("docs").rglob("*.md"):
    metrics = length_tool(doc.read_text(encoding="utf-8"))
    print(f"{doc}: {metrics['num_sentences']} sentences, {metrics['num_words']} words")
```

Scan an entire documentation set to identify sprawling sections or under-documented topics.

## Troubleshooting

- **`LookupError: Resource punkt_tab not found`** – Run `python -m nltk.downloader punkt_tab` ahead of time, especially in air-gapped deployments.
- **Unexpected character counts** – The tool excludes spaces; adjust the implementation if you need raw length including whitespace.
- **Non-English text** – NLTK’s default tokenizers target English. Swap in language-specific tokenizers if needed.

## License

`swarmauri_tool_textlength` is released under the Apache 2.0 License. See `LICENSE` for full details.
