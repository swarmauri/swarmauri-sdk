![Swarmauri](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
  <a href="https://pepy.tech/project/swarmauri_llm_azureopenai"><img src="https://static.pepy.tech/badge/swarmauri_llm_azureopenai/month" alt="Downloads"></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_azureopenai/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_azureopenai.svg" alt="Hits"></a>
  <a href="https://pypi.org/project/swarmauri_llm_azureopenai/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python"></a>
  <a href="https://pypi.org/project/swarmauri_llm_azureopenai/"><img src="https://img.shields.io/pypi/l/swarmauri_llm_azureopenai" alt="License"></a>
  <a href="https://pypi.org/project/swarmauri_llm_azureopenai/"><img src="https://img.shields.io/pypi/v/swarmauri_llm_azureopenai" alt="Release"></a>
</p>

# Swarmauri Azure OpenAI LLM

`swarmauri_llm_azureopenai` provides provider-native Swarmauri adapters for Azure OpenAI and Microsoft Foundry chat-completions deployments.

## Features

- `AzureOpenAIModel` directly implements the Swarmauri LLM base contract.
- `AzureOpenAIToolModel` directly implements the tool-LLM base contract.
- API-key authentication with Azure's `api-key` header.
- Refreshable Microsoft Entra bearer-token providers kept outside serialized state.
- Sync, async, streaming, and batch workflows against the current `/openai/v1` API.

## Installation

```bash
uv add swarmauri_llm_azureopenai
```

```bash
pip install swarmauri_llm_azureopenai
```

## Usage

```python
import os

from swarmauri_llm_azureopenai import AzureOpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(messages=[HumanMessage(content="Summarize this release.")])
model = AzureOpenAIModel(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    name="my-gpt-deployment",
)
model.predict(conversation)
print(conversation.get_last().content)
```

For keyless authentication, omit `api_key` and pass a callable as `token_provider`; it is invoked for every request so refreshed Entra tokens are used. Use `AzureOpenAIToolModel` with a Swarmauri `Toolkit` for function calling.

See the [Azure OpenAI chat REST reference](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/chat) and [Entra authentication guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-entra-id).
