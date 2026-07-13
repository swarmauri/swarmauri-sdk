![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_playht/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_playht/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_playht/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_playht.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_playht/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_playht/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_playht" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_playht/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_playht?label=swarmauri_llm_playht&color=green" alt="PyPI - swarmauri_llm_playht"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri PlayHT Legacy Compatibility

`swarmauri_llm_playht` preserves the historic `PlayHTModel` import while the
provider now lives in the standalone `swarmauri_tts_playht` package. The model
is a `TTSBase` component and is no longer registered as an LLM.

New applications should install and import `swarmauri_tts_playht` directly.

The adapter targets PlayHT's API under `https://api.play.ht/api/v2`, supports the repo-tracked model families `Play3.0-mini`, `PlayHT2.0-turbo`, `PlayHT1.0`, and `PlayHT2.0`, and writes generated audio to a local output file.

## Why Use This Package?

- Keep PlayHT-specific imports explicit in Swarmauri applications.
- Generate audio from text through a Swarmauri component instead of hand-writing PlayHT HTTP requests.
- Reuse one adapter for synthesis, cloned-voice discovery, and cloned-voice lifecycle operations.
- Bridge older `llms` usage to PlayHT’s speech-generation surface while newer TTS package paths continue to evolve.

## FAQ

### What does `swarmauri_llm_playht` install?

It installs `PlayHTModel` under `swarmauri.llms`.

### Is this actually a chat LLM package?

No. The runtime is a PlayHT text-to-speech adapter with voice-management helpers. The package name reflects the older export surface, but the behavior is speech generation rather than text chat.

### Which PlayHT model families are supported?

The current allowlist includes `Play3.0-mini`, `PlayHT2.0-turbo`, `PlayHT1.0`, and `PlayHT2.0`.

### What credentials are required?

You need a PlayHT API key and user ID. The runtime expects both `api_key` and `user_id`.

### Does it support streaming?

No. `stream` and `astream` are explicitly unimplemented for `PlayHTModel`.

### Can it manage cloned voices?

Yes. The adapter includes methods to get cloned voices, clone a voice from a file or URL, and delete a cloned voice.

## Features

- `PlayHTModel` for text-to-speech synthesis against the PlayHT API.
- Sync and async speech generation methods that save audio to a local file path.
- Batch and async batch synthesis workflows.
- Prebuilt voice discovery and validation for the selected voice engine.
- Cloned voice management helpers for create, list, and delete operations.
- A `swarmauri-playht` CLI for positional, piped, file-based, and interactive
  prompts through the stateless `TextToSpeechAgent`.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_playht
```

```bash
pip install swarmauri_llm_playht
```

## Usage

Set `PLAYHT_API_KEY` and `PLAYHT_USER_ID` in your environment before creating the model.

### Command Line

Set the credentials in your environment, then pass the text to synthesize:

```bash
export PLAYHT_API_KEY="your-api-key"
export PLAYHT_USER_ID="your-user-id"
swarmauri-playht "Welcome to Swarmauri." --output welcome.mp3
```

Run the command without text for an interactive prompt:

```bash
swarmauri-playht --output greeting.mp3
```

The CLI also accepts piped input or a UTF-8 prompt file:

```bash
echo "Turn this text into speech." | swarmauri-playht -o piped.mp3
swarmauri-playht --prompt-file script.txt --voice Adolfo -o narration.mp3
swarmauri-playht "Generate through the agent." \
  --voice-model PlayHT2.0-turbo -o agent.mp3
```

Use `swarmauri-playht --help` to see model, voice, timeout, and credential
options. Every command uses a fresh `TextToSpeechAgent` execution with no
conversation, memory, or system context. Environment variables are preferred
over credential flags so secrets do not remain in shell history.

### Text To Speech

```python
import os

from swarmauri_llm_playht import PlayHTModel

tts = PlayHTModel(
    api_key=os.environ["PLAYHT_API_KEY"],
    user_id=os.environ["PLAYHT_USER_ID"],
    name="Play3.0-mini",
    voice="Adolfo",
)

audio_path = tts.predict(
    "Swarmauri turns provider APIs into composable components.",
    audio_path="playht_output.mp3",
)

print(audio_path)
```

### Async Speech Generation

```python
import asyncio
import os

from swarmauri_llm_playht import PlayHTModel


async def main() -> None:
    tts = PlayHTModel(
        api_key=os.environ["PLAYHT_API_KEY"],
        user_id=os.environ["PLAYHT_USER_ID"],
        name="PlayHT2.0-turbo",
        voice="Adolfo",
    )
    output = await tts.apredict("Generate a short spoken greeting.", "greeting.mp3")
    print(output)


# asyncio.run(main())
```

### Voice Management

```python
import os

from swarmauri_llm_playht import PlayHTModel

tts = PlayHTModel(
    api_key=os.environ["PLAYHT_API_KEY"],
    user_id=os.environ["PLAYHT_USER_ID"],
    name="PlayHT2.0",
    voice="Adolfo",
)

voices = tts.get_cloned_voices()
print(voices)
```

## Examples

- Use `PlayHTModel` when an agent or application needs provider-hosted speech output saved to a local file.
- Use batch methods when one workflow needs multiple spoken outputs in one pass.
- Use cloned voice methods when the application manages a catalog of custom voices in PlayHT.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [PlayHT API docs](https://docs.play.ht/)
- [PlayHT generated API reference](https://playht.github.io/api-docs-generator/)

## Best Practices

- Keep `PLAYHT_API_KEY` and `PLAYHT_USER_ID` in environment variables or a secret manager.
- Validate the selected voice against the chosen PlayHT voice engine before running batch jobs.
- Use explicit output paths so generated audio assets are easy to manage.
- Prefer newer Swarmauri TTS-native imports when available for new projects, since this package preserves an older compatibility surface.

## License

Apache-2.0
