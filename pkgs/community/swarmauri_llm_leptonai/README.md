![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_llm_leptonai" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_leptonai.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_llm_leptonai" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_leptonai" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_leptonai/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_leptonai?label=swarmauri_llm_leptonai&color=green" alt="PyPI - swarmauri_llm_leptonai"/></a>
</p>

---

# Swarmauri LLM LeptonAI

Integration package for calling Lepton AI's hosted language and image generation models from Swarmauri agents. Ships LLM and image-gen adapters with synchronous, streaming, and asynchronous workflows that match Swarmauri conventions.

## Features

- Chat completion support for Lepton AI models (e.g., `llama3-8b`, `mixtral-8x7b`) with automatic usage tracking.
- Streaming and async token generation for latency-sensitive experiences.
- SDXL-based image generation with convenience helpers to save or display returned bytes.
- Single configuration surface for model name, base URL, and API key; reuse the same credential for both text and image endpoints.

## Prerequisites

- Python 3.10 or newer.
- A Lepton AI API key stored outside source control (environment variables or secret stores recommended).
- Network access to `*.lepton.run` endpoints; the `openai` Python client is installed automatically as a dependency.

## Installation

```bash
# pip
pip install swarmauri_llm_leptonai

# poetry
poetry add swarmauri_llm_leptonai

# uv (pyproject-based projects)
uv add swarmauri_llm_leptonai
```

## Quickstart: Chat Completions

```python
import os
from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

api_key = os.environ["LEPTON_API_KEY"]

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize Swarmauri in two sentences."))

model = LeptonAIModel(api_key=api_key, name="llama3-8b")
response = model.predict(conversation=conversation)

print(response.get_last().content)
print("Tokens used", response.get_last().usage.total_tokens)
```

### Async and Streaming

```python
import asyncio
import os
from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

async def ask_async(prompt: str) -> None:
    convo = Conversation()
    convo.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(api_key=os.environ["LEPTON_API_KEY"], name="mixtral-8x7b")
    result = await model.apredict(conversation=convo)
    print(result.get_last().content)

def stream_story(prompt: str) -> None:
    convo = Conversation()
    convo.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(api_key=os.environ["LEPTON_API_KEY"])
    for token in model.stream(conversation=convo):
        print(token, end="", flush=True)

# asyncio.run(ask_async("Draft a product announcement."))
# stream_story("Write a haiku about distributed agents.")
```

## Generate Images with SDXL

```python
import os
from pathlib import Path
from swarmauri_llm_leptonai import LeptonAIImgGenModel

img_model = LeptonAIImgGenModel(api_key=os.environ["LEPTON_API_KEY"], model_name="sdxl")

prompt = "A cyberpunk skyline at blue hour in watercolor style"
image_bytes = img_model.generate_image(prompt=prompt, width=768, height=512)

output = Path("leptonai_cyberpunk.png")
img_model.save_image(image_bytes, output.as_posix())

# Display in a notebook or desktop environment
# img_model.display_image(image_bytes)
```

## Operational Tips

- Models are invoked via `https://<model>.lepton.run/api/v1/`; updating `name` on `LeptonAIModel` switches endpoints without altering the client setup.
- Streaming responses emit usage data at stream completion; consume the generator fully before inspecting `conversation.get_last().usage`.
- Respect Lepton AI rate limits—add retries with exponential backoff or queue requests during traffic spikes.
- Store API keys securely and rotate them regularly; avoid hard-coding credentials in notebooks or scripts.
- Large image generations may take longer and consume more credits; adjust `width`, `height`, `steps`, and `guidance_scale` to balance quality versus latency.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
