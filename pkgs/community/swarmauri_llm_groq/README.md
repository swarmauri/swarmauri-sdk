![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri_brand_frag_light.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_groq" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_groq/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_groq.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_groq" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_groq" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_groq?label=swarmauri_llm_groq&color=green" alt="PyPI - swarmauri_llm_groq"/></a>
</p>

---

# swarmauri_llm_groq

Provider-specific Groq LLM package for Swarmauri. This package offers direct imports for GroqAIAudio, GroqModel, GroqToolModel, GroqVisionModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `GroqAIAudio` adapter exported from `swarmauri_standard.llms.GroqAIAudio`.
- `GroqModel` adapter exported from `swarmauri_standard.llms.GroqModel`.
- `GroqToolModel` adapter exported from `swarmauri_standard.llms.GroqToolModel`.
- `GroqVisionModel` adapter exported from `swarmauri_standard.llms.GroqVisionModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_groq

# pip
pip install swarmauri_llm_groq
```

## Usage

```python
from swarmauri_llm_groq import GroqAIAudio
from swarmauri_llm_groq import GroqModel
from swarmauri_llm_groq import GroqToolModel
from swarmauri_llm_groq import GroqVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = GroqAIAudio()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
