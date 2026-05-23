![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_hyperbolic/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_hyperbolic/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_hyperbolic/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_hyperbolic.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_hyperbolic" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_hyperbolic/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_hyperbolic?label=swarmauri_llm_hyperbolic&color=green" alt="PyPI - swarmauri_llm_hyperbolic"/></a>
</p>

# Swarmauri Hyperbolic LLM

`swarmauri_llm_hyperbolic` provides provider-specific imports for Hyperbolic
inference in Swarmauri applications. The package exports text chat,
vision-language, and text-to-speech adapters while keeping implementation parity
with `swarmauri_standard`.

Hyperbolic's inference documentation describes OpenAI-compatible chat
completion APIs under `https://api.hyperbolic.xyz/v1/chat/completions`, model
catalog discovery under `/v1/models`, vision-language models that accept images
alongside text, and audio generation through `/v1/audio/generation`. This
package maps those provider surfaces into Swarmauri components:

- `HyperbolicModel` for OpenAI-compatible text chat completions.
- `HyperbolicVisionModel` for vision-language chat completions with image input.
- `HyperbolicAudioTTS` for text-to-speech audio generation.

## Why Use This Package?

- Keep Hyperbolic-specific inference imports explicit in Swarmauri applications.
- Use Swarmauri `Conversation` objects with Hyperbolic's OpenAI-compatible chat
  and vision-language endpoints.
- Add text-to-speech generation without wiring raw base64 audio responses in
  application code.
- Preserve a provider package boundary while relying on shared
  `swarmauri_standard` runtime implementations.

## FAQ

### What does `swarmauri_llm_hyperbolic` install?

It installs provider package entry points for `HyperbolicModel`,
`HyperbolicVisionModel`, and `HyperbolicAudioTTS`.

### Which Hyperbolic endpoints does it use?

`HyperbolicModel` and `HyperbolicVisionModel` use Hyperbolic's
OpenAI-compatible `chat/completions` endpoint. `HyperbolicAudioTTS` posts to
`https://api.hyperbolic.xyz/v1/audio/generation` and writes the returned base64
audio payload to a local file.

### Does it support streaming?

`HyperbolicModel` supports synchronous and asynchronous streaming for chat
completion responses. `HyperbolicAudioTTS` does not support streaming and raises
`NotImplementedError` for `stream` and `astream`.

### Does it support vision-language prompts?

Yes. `HyperbolicVisionModel` accepts Swarmauri message content lists with text
and image input. Local image file paths can be converted to base64 data URLs by
the runtime helper.

### Is the TTS adapter a general LLM?

No. `HyperbolicAudioTTS` is a text-to-speech adapter kept in this provider
package for compatibility. The runtime deprecation warning points new projects
toward newer Swarmauri TTS imports when available.

## Features

- `HyperbolicModel` for sync, async, streaming, and batch chat completion
  workflows.
- `HyperbolicVisionModel` for image-plus-text prompts against Hyperbolic VLMs.
- `HyperbolicAudioTTS` for synchronous and asynchronous text-to-speech
  generation.
- Model discovery through Hyperbolic's `/models` endpoint.
- Generation controls including `temperature`, `max_tokens`, `top_p`, `top_k`,
  and `stop`.
- Optional usage metadata handling on chat responses when available.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_hyperbolic
```

```bash
pip install swarmauri_llm_hyperbolic
```

## Prerequisites

Create a Hyperbolic API key in the Hyperbolic app and pass it to the model
constructor as `api_key=...`.

## Usage

```python
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize this deployment risk."))

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming Chat

```python
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three API gateway checks."))

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

### Vision-Language Prompt

```python
from swarmauri_llm_hyperbolic import HyperbolicVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(
        content=[
            {"type": "text", "text": "Describe the image."},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
        ]
    )
)

model = HyperbolicVisionModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

### Text To Speech

```python
from swarmauri_llm_hyperbolic import HyperbolicAudioTTS

tts = HyperbolicAudioTTS(
    api_key="HYPERBOLIC_API_KEY",
    language="EN",
    speaker="EN-US",
    speed=1.0,
)

audio_path = tts.predict("Swarmauri turns model providers into components.")
print(audio_path)
```

## Related Packages

- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_playht](https://pypi.org/project/swarmauri_llm_playht/)

## Foundational Swarmauri Packages

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

## Provider Documentation

- [Hyperbolic quick start](https://www.hyperbolic.ai/docs/inference/quickstart)
- [Hyperbolic text generation APIs](https://www.hyperbolic.ai/docs/inference/text-apis)
- [Hyperbolic vision-language APIs](https://www.hyperbolic.ai/docs/inference/vlm-apis)
- [Hyperbolic supported models](https://docs.hyperbolic.xyz/docs/supported-models)

## Best Practices

- Store Hyperbolic API keys in environment variables or a secrets manager.
- Confirm model availability and provider capability flags before production
  deployment.
- Use `HyperbolicVisionModel` only for image-aware prompts; plain chat is simpler
  with `HyperbolicModel`.
- Use explicit output paths for TTS generation so generated audio files are easy
  to manage.
- Prefer newer Swarmauri VLM and TTS imports for new projects when available.

## License

Apache-2.0
