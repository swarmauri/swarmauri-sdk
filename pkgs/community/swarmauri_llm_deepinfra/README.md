![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_deepinfra/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_deepinfra/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_deepinfra/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_deepinfra.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepinfra/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepinfra/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_deepinfra" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepinfra/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_deepinfra?label=swarmauri_llm_deepinfra&color=green" alt="PyPI - swarmauri_llm_deepinfra"/></a>
</p>

# Swarmauri DeepInfra LLM

`swarmauri_llm_deepinfra` provides the `DeepInfraModel` import path for Swarmauri applications that use DeepInfra's OpenAI-compatible chat completions API. The package re-exports the maintained implementation from `swarmauri_standard`, giving projects a provider-specific dependency for hosted open-source LLM inference through Swarmauri conversations.

## Why Swarmauri DeepInfra LLM?

Use this package when you want DeepInfra-hosted models behind the Swarmauri `LLMBase` interface. `DeepInfraModel` formats Swarmauri messages for OpenAI-compatible chat completions, supports sync and async prediction, streams response chunks, runs sequential and concurrent batches, supports stop sequences, and can request JSON-object responses on compatible models.

## FAQ

### Q: Which DeepInfra endpoint does this adapter call?

A: The adapter uses `https://api.deepinfra.com/v1/openai/chat/completions`, DeepInfra's OpenAI-compatible chat completions endpoint.

### Q: Which model names are configured locally?

A: The local allowed-model list includes models such as `Qwen/Qwen2-72B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`, `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `mistralai/Mixtral-8x7B-Instruct-v0.1`, `codellama/CodeLlama-70b-Instruct-hf`, and other DeepInfra model identifiers. The default is `01-ai/Yi-34B-Chat`.

### Q: Does this package contain a separate DeepInfra implementation?

A: No. It re-exports `DeepInfraModel` from `swarmauri_standard.llms.DeepInfraModel` so applications can depend on this provider package while sharing the common implementation.

### Q: How does JSON mode work?

A: Pass `enable_json=True` to `predict()`, `apredict()`, `batch()`, or `abatch()`. The adapter sends `response_format={"type": "json_object"}` to the OpenAI-compatible endpoint.

## Features

- Provider-specific import: `from swarmauri_llm_deepinfra import DeepInfraModel`.
- Swarmauri `Conversation`, `HumanMessage`, `SystemMessage`, and `AgentMessage` integration.
- Sync `predict()` and async `apredict()` chat completion calls.
- Sync `stream()` and async `astream()` SSE-style streaming.
- Sync `batch()` and async `abatch()` helpers.
- Configurable `temperature`, `max_tokens`, `stop`, and `enable_json`.
- OpenAI-compatible request fields: `messages`, `top_p`, `frequency_penalty`, `presence_penalty`, and `stream`.
- Model discovery through the DeepInfra `/models` endpoint.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- DeepInfra API key.
- Network access to `api.deepinfra.com`.
- A DeepInfra model ID that supports chat completions.
- Swarmauri conversations built from Swarmauri message classes.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_deepinfra
```

Install with `pip`:

```bash
pip install swarmauri_llm_deepinfra
```

## Usage

Run a DeepInfra chat completion:

```python
import os

from swarmauri_llm_deepinfra import DeepInfraModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(SystemMessage(content="Answer with concise technical prose."))
conversation.add_message(HumanMessage(content="What is DeepInfra?"))

model = DeepInfraModel(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="Qwen/Qwen2.5-72B-Instruct",
)
result = model.predict(conversation=conversation, temperature=0.2, max_tokens=256)

print(result.get_last().content)
```

Stream response chunks:

```python
import os

from swarmauri_llm_deepinfra import DeepInfraModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Draft a short model card summary."))

model = DeepInfraModel(api_key=os.environ["DEEPINFRA_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

Request JSON output:

```python
import os

from swarmauri_llm_deepinfra import DeepInfraModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content='Return {"status": "ok"} as JSON.'))

model = DeepInfraModel(api_key=os.environ["DEEPINFRA_API_KEY"])
result = model.predict(conversation=conversation, enable_json=True)

print(result.get_last().content)
```

## Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared `DeepInfraModel` implementation.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store `DEEPINFRA_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly because hosted model availability can change.
- Validate JSON-mode behavior on the exact model you deploy.
- Use async methods for high-concurrency workloads.
- Keep stop sequences close to the prompt design that was tested for a given model.

## License

Apache-2.0
