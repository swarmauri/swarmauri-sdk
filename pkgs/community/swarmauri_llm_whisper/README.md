![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_whisper/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_whisper/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_whisper/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_whisper.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_whisper" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_whisper/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_whisper?label=swarmauri_llm_whisper&color=green" alt="PyPI - swarmauri_llm_whisper"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Whisper Transcription

`swarmauri_llm_whisper` provides the provider-specific Swarmauri import package for `WhisperLargeModel`. Despite the older `llm` package name, the runtime is a speech-to-text adapter that calls Hugging Face Inference for `openai/whisper-large-v3` and supports both transcription and translation workflows.

The adapter targets Hugging Face Inference at `https://api-inference.huggingface.co/models/openai/whisper-large-v3`, accepts local audio file paths, and returns text output for single-file, async, and batch processing workflows.

## Why Use This Package?

- Keep Whisper-specific imports explicit in Swarmauri applications.
- Transcribe or translate audio through a Swarmauri component instead of hand-writing Hugging Face Inference requests.
- Reuse one adapter for synchronous, asynchronous, and batch audio processing.
- Bridge older `llms` import patterns while newer `stt`-oriented package paths continue to evolve.

## FAQ

### What does `swarmauri_llm_whisper` install?

It installs `WhisperLargeModel` under `swarmauri.llms`.

### Is this a chat LLM package?

No. The runtime is a speech-to-text adapter for `openai/whisper-large-v3` on Hugging Face Inference.

### Which tasks are supported?

The adapter supports `transcription` and `translation`.

### Which model is supported today?

The current runtime allowlist contains `openai/whisper-large-v3`.

### Does it support streaming?

No. `stream` and `astream` are explicitly unimplemented for this adapter.

### What credentials are required?

You need a Hugging Face access token with permission to use the target inference surface.

## Features

- `WhisperLargeModel` for transcription and translation against Hugging Face Inference.
- Sync and async single-file processing.
- Batch and async batch audio workflows.
- Explicit task selection between transcription and translation.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_whisper
```

```bash
pip install swarmauri_llm_whisper
```

## Usage

Set `HF_API_KEY` in your environment before creating the model.

### Transcription

```python
import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test.mp3", task="transcription")

print(text)
```

### Translation

```python
import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test_fr.mp3", task="translation")

print(text)
```

### Async Batch Processing

```python
import asyncio
import os

from swarmauri_llm_whisper import WhisperLargeModel


async def main() -> None:
    model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
    results = await model.abatch(
        {
            "tests/static/test.mp3": "transcription",
            "tests/static/test_fr.mp3": "translation",
        }
    )
    print(results)


# asyncio.run(main())
```

## Examples

- Use `transcription` when the output should stay in the original spoken language.
- Use `translation` when the output should be translated into English.
- Use batch methods when one job needs to process multiple audio files together.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_playht](https://pypi.org/project/swarmauri_llm_playht/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_llamacpp](https://pypi.org/project/swarmauri_llm_llamacpp/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [openai/whisper-large-v3 model card](https://huggingface.co/openai/whisper-large-v3)
- [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/index)

## Best Practices

- Keep `HF_API_KEY` in environment variables or a secret manager.
- Choose `translation` only when English output is the intended downstream behavior.
- Use explicit local audio file paths and validate the file exists before dispatching a batch job.
- Prefer newer Swarmauri STT-native imports when available for new projects, since this package preserves an older compatibility surface.

## License

Apache-2.0
