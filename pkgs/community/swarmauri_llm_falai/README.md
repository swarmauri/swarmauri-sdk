![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_falai/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_falai/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_falai/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_falai.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_falai/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_falai/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_falai" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_falai/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_falai?label=swarmauri_llm_falai&color=green" alt="PyPI - swarmauri_llm_falai"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri fal.ai Vision Model

`swarmauri_llm_falai` provides the provider-specific `FalAIVisionModel`
import for Swarmauri projects that call fal.ai vision and image-understanding
models. The adapter accepts an image URL plus a prompt, submits the request to
fal's queue-backed inference API, polls for completion, and returns the model
output string.

This package preserves the legacy LLM-package import path for fal.ai vision
workloads while keeping implementation parity with
`swarmauri_standard.llms.FalAIVisionModel`. New VLM-oriented code should also
review the newer Swarmauri VLM imports mentioned by the runtime deprecation
warning.

fal.ai's public documentation describes queue-backed inference under
`https://queue.fal.run/{model_id}`, including request submission, status polling,
and response retrieval. That maps directly to this adapter's `predict` and
`apredict` workflows.

## Why Use This Package?

- Keep fal.ai-specific vision model dependencies isolated from the rest of a
  Swarmauri application.
- Ask questions about remote images with Swarmauri-style model components.
- Use fal's queue-backed inference lifecycle without writing queue polling logic
  in application code.
- Preserve compatibility for projects that still import `FalAIVisionModel` from
  the LLM provider package.

## FAQ

### What does `swarmauri_llm_falai` install?

It installs a provider package that exports `FalAIVisionModel` from
`swarmauri_standard.llms.FalAIVisionModel` and registers it under the Swarmauri
LLM entry point group.

### Is this a text-only LLM package?

No. The model accepts `image_url` and `prompt` arguments and is intended for
vision-language tasks such as OCR, image captioning, visual question answering,
and image moderation workflows supported by fal.ai models.

### Which fal.ai endpoint does it use?

The adapter posts to `https://queue.fal.run/{model_id}`. When fal returns a
`request_id`, the adapter polls the corresponding request status endpoint until
the request is completed, then fetches the response URL.

### Which environment variable can supply credentials?

The model default reads `FAL_KEY` when `api_key` is not passed explicitly. The
package tests also support live checks when a fal.ai key is available.

### Does this adapter support streaming?

No. `stream` and `astream` intentionally raise `NotImplementedError` for
`FalAIVisionModel`.

## Features

- Provider-specific `FalAIVisionModel` import for Swarmauri projects.
- Vision-language prediction with `image_url` and `prompt` inputs.
- Queue-backed request submission and status polling through fal.ai.
- Synchronous prediction through `predict`.
- Asynchronous prediction through `apredict`.
- Configurable queue polling with `max_retries` and `retry_delay`.
- Built-in model allow list covering OCR, LLaVA, Florence, Moondream, MiniCPM,
  SA2VA, and related fal.ai vision endpoints.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_falai
```

```bash
pip install swarmauri_llm_falai
```

## Prerequisites

Create a fal.ai API key and provide it as `FalAIVisionModel(api_key=...)` or set
`FAL_KEY` in the runtime environment.

## Usage

```python
from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY")

answer = model.predict(
    image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
    prompt="Who painted this artwork?",
)

print(answer)
```

### Async Vision Question Answering

```python
import asyncio

from swarmauri_llm_falai import FalAIVisionModel


async def main() -> None:
    model = FalAIVisionModel(api_key="FAL_KEY")
    answer = await model.apredict(
        image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
        prompt="Describe the subject of the painting.",
    )
    print(answer)


asyncio.run(main())
```

### Choose A fal.ai Vision Model

```python
from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY", name="fal-ai/florence-2-large/ocr")

text = model.predict(
    image_url="https://example.com/document-scan.png",
    prompt="Extract the visible text.",
)

print(text)
```

## Related Packages

- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_pytesseractimg2text](https://pypi.org/project/swarmauri_llm_pytesseractimg2text/)
- [swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)

## Foundational Swarmauri Packages

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

## Provider Documentation

- [fal.ai asynchronous inference](https://fal.ai/docs/documentation/model-apis/inference/queue)
- [fal.ai synchronous inference](https://fal.ai/docs/documentation/model-apis/inference/synchronous)
- [fal.ai vision models](https://fal.ai/models?categories=vision)

## Best Practices

- Store fal.ai credentials in environment variables or a secrets manager.
- Use image URLs that are reachable by the fal.ai runtime.
- Tune `max_retries` and `retry_delay` for long-running queue-backed models.
- Prefer newer Swarmauri VLM imports for new projects when available.

## License

Apache-2.0


