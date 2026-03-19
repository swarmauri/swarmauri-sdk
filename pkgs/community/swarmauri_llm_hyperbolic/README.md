![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_hyperbolic" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_hyperbolic/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_hyperbolic.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_hyperbolic" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_hyperbolic" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_hyperbolic?label=swarmauri_llm_hyperbolic&color=green" alt="PyPI - swarmauri_llm_hyperbolic"/></a>
</p>

---

# swarmauri_llm_hyperbolic

Provider-specific Hyperbolic LLM package for Swarmauri. This package offers direct imports for HyperbolicAudioTTS, HyperbolicModel, HyperbolicVisionModel while keeping implementation parity with `swarmauri_standard`.

## Features

- `HyperbolicAudioTTS` adapter exported from `swarmauri_standard.llms.HyperbolicAudioTTS`.
- `HyperbolicModel` adapter exported from `swarmauri_standard.llms.HyperbolicModel`.
- `HyperbolicVisionModel` adapter exported from `swarmauri_standard.llms.HyperbolicVisionModel`.
- Compatible with Python 3.10 through 3.12.

## Installation

```bash
# uv
uv add swarmauri_llm_hyperbolic

# pip
pip install swarmauri_llm_hyperbolic
```

## Usage

```python
from swarmauri_llm_hyperbolic import HyperbolicAudioTTS
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_llm_hyperbolic import HyperbolicVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Hello from Swarmauri"))

model = HyperbolicAudioTTS()
# Configure provider credentials before making requests.
# result = model.predict(conversation=conversation)
```

## Workflow Notes

- These adapters intentionally mirror the corresponding classes in `swarmauri_standard`.
- Use the provider package that matches your deployment and credential setup.
- Install only the provider packages you need to keep dependencies minimal.
