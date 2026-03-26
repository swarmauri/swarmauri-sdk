![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_mistral" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_mistral/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_mistral.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_mistral" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_mistral" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_mistral?label=swarmauri_llm_mistral&color=green" alt="PyPI - swarmauri_llm_mistral"/></a>
</p>

---

# swarmauri_llm_mistral

Provider-specific Mistral LLM package for Swarmauri. This package offers direct imports for MistralModel, MistralToolModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `MistralModel` adapter exported from `swarmauri_standard.llms.MistralModel`.
- `MistralToolModel` adapter exported from `swarmauri_standard.llms.MistralToolModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_mistral

# pip
pip install swarmauri_llm_mistral
```

## Usage

```python
from swarmauri_llm_mistral import MistralModel
from swarmauri_llm_mistral import MistralToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = MistralModel()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
