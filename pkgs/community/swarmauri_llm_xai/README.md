![Swarmauri](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
  <a href="https://pepy.tech/project/swarmauri_llm_xai"><img src="https://static.pepy.tech/badge/swarmauri_llm_xai/month" alt="Downloads"></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_xai/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_xai.svg" alt="Hits"></a>
  <a href="https://pypi.org/project/swarmauri_llm_xai/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python"></a>
  <a href="https://pypi.org/project/swarmauri_llm_xai/"><img src="https://img.shields.io/pypi/l/swarmauri_llm_xai" alt="License"></a>
  <a href="https://pypi.org/project/swarmauri_llm_xai/"><img src="https://img.shields.io/pypi/v/swarmauri_llm_xai" alt="Release"></a>
</p>

# Swarmauri xAI LLM

`swarmauri_llm_xai` provides provider-native Swarmauri adapters for xAI's Grok chat-completions API.

## Features

- `XAIModel` directly implements the Swarmauri LLM base contract.
- `XAIToolModel` directly implements the tool-LLM base contract.
- Bearer-token authentication with credentials excluded from serialized state.
- Sync, async, incremental streaming, batch, and function-calling workflows.
- Optional model discovery through xAI's language-model catalog.

## Installation

```bash
uv add swarmauri_llm_xai
```

```bash
pip install swarmauri_llm_xai
```

## Usage

```python
import os

from swarmauri_llm_xai import XAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(messages=[HumanMessage(content="Explain orbital mechanics briefly.")])
model = XAIModel(api_key=os.environ["XAI_API_KEY"], name="grok-4.3")
model.predict(conversation)
print(conversation.get_last().content)
```

Use `XAIToolModel` with a Swarmauri `Toolkit` for function calling. Set `discover_models=True` to populate allowed model IDs from the authenticated xAI language-model catalog.

See the [xAI inference reference](https://docs.x.ai/developers/rest-api-reference/inference), [chat endpoint](https://docs.x.ai/developers/rest-api-reference/inference/chat), and [function-calling guide](https://docs.x.ai/developers/tools/function-calling).
