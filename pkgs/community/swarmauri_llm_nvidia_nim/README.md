![Swarmauri](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
  <a href="https://pepy.tech/project/swarmauri_llm_nvidia_nim"><img src="https://static.pepy.tech/badge/swarmauri_llm_nvidia_nim/month" alt="Downloads"></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_nvidia_nim/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_nvidia_nim.svg" alt="Hits"></a>
  <a href="https://pypi.org/project/swarmauri_llm_nvidia_nim/"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python"></a>
  <a href="https://pypi.org/project/swarmauri_llm_nvidia_nim/"><img src="https://img.shields.io/pypi/l/swarmauri_llm_nvidia_nim" alt="License"></a>
  <a href="https://pypi.org/project/swarmauri_llm_nvidia_nim/"><img src="https://img.shields.io/pypi/v/swarmauri_llm_nvidia_nim" alt="Release"></a>
</p>

# Swarmauri NVIDIA NIM LLM

`swarmauri_llm_nvidia_nim` connects Swarmauri conversations and toolkits to an NVIDIA NIM for LLMs deployment.

## Features

- OpenAI-compatible chat completions through `NvidiaNIMModel`.
- Tool calling through `NvidiaNIMToolModel`.
- Synchronous, asynchronous, incremental streaming, and batch workflows inherited from Swarmauri's shared transports.
- Optional discovery from the deployment's `/v1/models` endpoint.
- Configurable deployment base URL for local, private, and managed NIM endpoints.

## Installation

```bash
uv add swarmauri_llm_nvidia_nim
```

```bash
pip install swarmauri_llm_nvidia_nim
```

## Usage

```python
from swarmauri_llm_nvidia_nim import NvidiaNIMModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(messages=[HumanMessage(content="What is accelerated computing?")])
model = NvidiaNIMModel(
    base_url="http://localhost:8000",
    name="meta/llama-3.1-8b-instruct",
)
model.predict(conversation)
print(conversation.get_last().content)
```

Pass `api_key` when the deployment requires bearer authentication. Set `discover_models=True` to populate `allowed_models` from the running deployment. For tool workflows, instantiate `NvidiaNIMToolModel` and pass a Swarmauri `Toolkit` to `predict`, `apredict`, `stream`, or `astream`.

See the [NVIDIA NIM LLM API reference](https://docs.nvidia.com/nim/large-language-models/latest/reference/api-reference.html) for deployment and model-specific capability details.
