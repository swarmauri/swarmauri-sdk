![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_perplexity/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_perplexity/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_perplexity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_perplexity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_perplexity/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_perplexity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_perplexity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_perplexity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_perplexity?label=swarmauri_llm_perplexity&color=green" alt="PyPI - swarmauri_llm_perplexity"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Perplexity LLM

`swarmauri_llm_perplexity` provides the provider-specific Swarmauri import package for `PerplexityModel`. It wraps Perplexity's chat completion API so Swarmauri applications can use the tracked `sonar` and `r1-1776` model families through the standard `Conversation` workflow.

The runtime targets `https://api.perplexity.ai/chat/completions`, supports sync, async, streaming, and batch generation, and exposes controls such as `return_citations`, `top_p`, `top_k`, `presence_penalty`, and `frequency_penalty`.

## Why Use This Package?

- Keep Perplexity-specific imports explicit in Swarmauri applications.
- Use Swarmauri `Conversation` objects against Perplexity's hosted chat completion API.
- Stream Perplexity responses while preserving the same component model used across other provider packages.
- Access Perplexity's current repo-tracked `sonar` and reasoning model families from a dedicated package boundary.

## FAQ

### What does `swarmauri_llm_perplexity` install?

It installs `PerplexityModel` under `swarmauri.llms`.

### Which Perplexity model families are tracked?

The current runtime allowlist includes `sonar-deep-research`, `sonar-reasoning-pro`, `sonar-reasoning`, `sonar-pro`, `sonar`, and `r1-1776`.

### Does the package support streaming?

Yes. `PerplexityModel` supports `predict`, `apredict`, `stream`, `astream`, `batch`, and `abatch`.

### Can it request citations?

Yes. The runtime exposes a `return_citations` option so the provider can include citation data when supported by the selected model.

### Can I set both `top_p` and `top_k`?

No. The runtime rejects that combination and raises a `ValueError`.

### Where should I verify current model and pricing details?

Use the Perplexity section in [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md), which links to the current model cards and pricing documentation.

## Features

- `PerplexityModel` import package for hosted Perplexity chat completion workflows.
- Sync, async, streaming, and batch generation support.
- Optional citation-return behavior for supported Perplexity responses.
- Usage metadata capture through Swarmauri `UsageData` when enabled.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_perplexity
```

```bash
pip install swarmauri_llm_perplexity
```

## Usage

Set `PPLX_API_KEY` in your environment before creating the model.

### Chat Completion

```python
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize Swarmauri in two sentences."))

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming

```python
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three differences between hosted and local inference."))

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar-reasoning",
)

for token in model.stream(conversation=conversation, return_citations=True):
    print(token, end="", flush=True)
```

### Async

```python
import asyncio
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Explain retrieval-augmented generation briefly."))

    model = PerplexityModel(
        api_key=os.environ["PPLX_API_KEY"],
        name="sonar-pro",
    )
    result = await model.apredict(conversation=conversation, return_citations=True)
    print(result.get_last().content)


# asyncio.run(main())
```

## Examples

- Use `sonar` for general-purpose hosted Perplexity chat workflows.
- Use `sonar-reasoning` or `sonar-reasoning-pro` when you want the reasoning-oriented family explicitly.
- Use `return_citations=True` when the downstream experience should expose provider citations alongside the generated response.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_playht](https://pypi.org/project/swarmauri_llm_playht/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [Perplexity model cards](https://docs.perplexity.ai/guides/model-cards)
- [Perplexity pricing](https://docs.perplexity.ai/docs/getting-started/pricing)

## Best Practices

- Keep `PPLX_API_KEY` in environment variables or a secret manager.
- Choose the Perplexity model family intentionally, especially when switching between search-style and reasoning-oriented variants.
- Do not set both `top_p` and `top_k` in the same request.
- Use citation-return mode only when the consuming application is prepared to surface or process citation metadata.

## License

Apache-2.0


