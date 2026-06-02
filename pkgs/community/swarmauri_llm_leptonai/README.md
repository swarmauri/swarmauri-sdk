![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_leptonai/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_leptonai/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_leptonai" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_leptonai?label=swarmauri_llm_leptonai&color=green" alt="PyPI - swarmauri_llm_leptonai"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri LeptonAI LLM

`swarmauri_llm_leptonai` provides provider-specific Swarmauri imports for Lepton AI hosted chat models and SDXL image generation. The package exposes `LeptonAIModel` for synchronous, asynchronous, streaming, and batch text generation workflows, plus `LeptonAIImgGenModel` for prompt-to-image generation against Lepton-hosted image endpoints.

The runtime uses model-specific Lepton endpoints in the form `https://<model>.lepton.run/api/v1/` for chat and `https://sdxl.lepton.run/run` for image generation. That keeps Lepton-specific configuration isolated in one provider package while preserving the shared Swarmauri `Conversation` and component model.

## Why Use This Package?

- Keep Lepton AI imports explicit in Swarmauri applications instead of importing provider implementations from broader runtime packages.
- Run hosted chat models with sync, async, streaming, and batch interfaces that align with Swarmauri LLM conventions.
- Generate images with a Swarmauri image generation component instead of managing raw HTTP calls directly.
- Reuse shared Swarmauri message, conversation, and serialization behavior while keeping provider credentials and model names local to the Lepton package.

## FAQ

### What does `swarmauri_llm_leptonai` install?

It installs two provider entry points: `LeptonAIModel` under `swarmauri.llms` and `LeptonAIImgGenModel` under `swarmauri.image_gens`.

### Which Lepton AI capabilities are wrapped today?

The package currently wraps hosted chat completion style inference for the allowlisted text models in `LeptonAIModel` and SDXL image generation through `LeptonAIImgGenModel`.

### Does `LeptonAIModel` support streaming and async workflows?

Yes. `LeptonAIModel` supports `predict`, `apredict`, `stream`, `astream`, `batch`, and `abatch`.

### How does model selection work?

`LeptonAIModel` builds its base URL from the configured `name`, so changing `name="llama3-8b"` to another allowlisted model switches the Lepton endpoint without changing the rest of the application code.

### Does the image generator support batch workflows?

Yes. `LeptonAIImgGenModel` supports `generate_image`, `agenerate_image`, `batch_generate`, and `abatch_generate`.

### Where should I verify current provider model availability and pricing?

Lepton's public model and pricing documentation is limited compared with other providers. Use the provider-facing surfaces in the Lepton dashboard and review [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md) for the current project-level documentation links before publishing model or pricing claims.

## Features

- `LeptonAIModel` for provider-hosted chat generation with sync, async, streaming, and batch execution.
- Usage metadata capture on text responses through Swarmauri `UsageData`.
- `LeptonAIImgGenModel` for prompt-to-image generation against Lepton-hosted SDXL endpoints.
- Endpoint selection derived from the configured model name for text generation workflows.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_leptonai
```

```bash
pip install swarmauri_llm_leptonai
```

## Usage

Set `LEPTON_API_KEY` in your environment before creating either component.

### Chat Completion

```python
import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize Swarmauri in two sentences."))

model = LeptonAIModel(
    api_key=os.environ["LEPTON_API_KEY"],
    name="llama3-8b",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
print(result.get_last().usage.total_tokens)
```

### Async and Streaming

```python
import asyncio
import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def ask_async(prompt: str) -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(
        api_key=os.environ["LEPTON_API_KEY"],
        name="mixtral-8x7b",
    )
    result = await model.apredict(conversation=conversation)
    print(result.get_last().content)


def stream_text(prompt: str) -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(api_key=os.environ["LEPTON_API_KEY"])
    for token in model.stream(conversation=conversation):
        print(token, end="", flush=True)


# asyncio.run(ask_async("Draft a short release note."))
# stream_text("Write a haiku about composable AI systems.")
```

### Image Generation

```python
import os
from pathlib import Path

from swarmauri_llm_leptonai import LeptonAIImgGenModel

image_model = LeptonAIImgGenModel(
    api_key=os.environ["LEPTON_API_KEY"],
    model_name="sdxl",
)

image_bytes = image_model.generate_image(
    prompt="A cyberpunk skyline at blue hour in watercolor style",
    width=768,
    height=512,
)

output = Path("leptonai_cyberpunk.png")
image_model.save_image(image_bytes, output.as_posix())
```

## Examples

- Use `LeptonAIModel` for provider-hosted chat inference when you want Swarmauri `Conversation` objects and token usage data.
- Use `LeptonAIImgGenModel` when an agent or application needs image generation without adding a separate provider package.
- Use `stream` or `astream` for latency-sensitive user interfaces that render tokens incrementally.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_falai](https://pypi.org/project/swarmauri_llm_falai/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [Lepton AI playground](https://www.lepton.ai/playground)

## Best Practices

- Keep `LEPTON_API_KEY` in environment variables or a secret manager.
- Validate current provider model availability before deploying a specific allowlisted model to production.
- Tune `width`, `height`, `steps`, and `guidance_scale` carefully for image generation to balance quality, latency, and cost.
- Consume full streaming responses before reading usage metadata from the final conversation message.

## License

Apache-2.0


