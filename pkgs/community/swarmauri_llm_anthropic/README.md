![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_anthropic/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_anthropic/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_anthropic/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_anthropic.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_anthropic" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_anthropic" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_anthropic?label=swarmauri_llm_anthropic&color=green" alt="PyPI - swarmauri_llm_anthropic"/></a>
</p>

---

# swarmauri_llm_anthropic

Provider-specific Anthropic LLM package for Swarmauri. This package offers direct imports for AnthropicModel, AnthropicToolModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `AnthropicModel` adapter exported from `swarmauri_standard.llms.AnthropicModel`.
- `AnthropicToolModel` adapter exported from `swarmauri_standard.llms.AnthropicToolModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_anthropic

# pip
pip install swarmauri_llm_anthropic
```

## Usage

```python
from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_llm_anthropic import AnthropicToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = AnthropicModel()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
