![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_ai21" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_ai21/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_ai21.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_ai21" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_ai21" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_ai21?label=swarmauri_llm_ai21&color=green" alt="PyPI - swarmauri_llm_ai21"/></a>
</p>

---

# swarmauri_llm_ai21

Provider-specific Ai21 LLM package for Swarmauri. This package offers direct imports for AI21StudioModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `AI21StudioModel` adapter exported from `swarmauri_standard.llms.AI21StudioModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_ai21

# pip
pip install swarmauri_llm_ai21
```

## Usage

```python
from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = AI21StudioModel()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
