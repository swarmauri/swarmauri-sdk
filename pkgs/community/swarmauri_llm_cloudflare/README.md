![Swarmauri](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
  <a href="https://pepy.tech/project/swarmauri_llm_cloudflare"><img src="https://static.pepy.tech/badge/swarmauri_llm_cloudflare/month" alt="Downloads"></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cloudflare/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cloudflare.svg" alt="Hits"></a>
  <a href="https://pypi.org/project/swarmauri_llm_cloudflare/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python"></a>
  <a href="https://pypi.org/project/swarmauri_llm_cloudflare/"><img src="https://img.shields.io/pypi/l/swarmauri_llm_cloudflare" alt="License"></a>
  <a href="https://pypi.org/project/swarmauri_llm_cloudflare/"><img src="https://img.shields.io/pypi/v/swarmauri_llm_cloudflare" alt="Release"></a>
</p>

# Swarmauri Cloudflare Workers AI LLM

`swarmauri_llm_cloudflare` connects Swarmauri conversations and toolkits to Cloudflare Workers AI's account-scoped REST API.

## Features

- OpenAI-compatible chat completions through `CloudflareWorkersAIModel`.
- Tool calling through `CloudflareWorkersAIToolModel` for models that advertise tool support.
- Synchronous, asynchronous, incremental streaming, and batch workflows.
- Optional discovery from Cloudflare's model-search endpoint.
- Explicit account ID and API-token configuration.

## Installation

```bash
uv add swarmauri_llm_cloudflare
```

```bash
pip install swarmauri_llm_cloudflare
```

## Usage

```python
import os

from swarmauri_llm_cloudflare import CloudflareWorkersAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(messages=[HumanMessage(content="Explain edge inference.")])
model = CloudflareWorkersAIModel(
    account_id=os.environ["CLOUDFLARE_ACCOUNT_ID"],
    api_key=os.environ["CLOUDFLARE_API_TOKEN"],
    name="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
)
model.predict(conversation)
print(conversation.get_last().content)
```

Set `discover_models=True` to query the current Workers AI model catalog. For tools, instantiate `CloudflareWorkersAIToolModel` with a tool-capable model and pass a Swarmauri `Toolkit`.

See the [Cloudflare Workers AI REST guide](https://developers.cloudflare.com/workers-ai/get-started/rest-api/) and [model-search API](https://developers.cloudflare.com/api/resources/ai/subresources/models/methods/list/) for account setup and current model details.
