![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_whisper/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_whisper/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_whisper/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_whisper.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_whisper" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_whisper?label=swarmauri_llm_whisper&color=green" alt="PyPI - swarmauri_llm_whisper"/></a>
</p>
---

# swarmauri_llm_whisper

Provider-specific Whisper LLM package for Swarmauri. This package offers direct imports for WhisperLargeModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `WhisperLargeModel` adapter exported from `swarmauri_standard.llms.WhisperLargeModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_whisper

# pip
pip install swarmauri_llm_whisper
```

## Usage

```python
from swarmauri_llm_whisper import WhisperLargeModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = WhisperLargeModel()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
