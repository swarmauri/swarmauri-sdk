![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_gemini

Alpha Swarmauri Gemini speech provider. Single-speaker Gemini 3.8 Interactions API. Older generateContent models, multi-speaker dialogue, voice management and Gemini Live are excluded.

[![Downloads](https://static.pepy.tech/badge/swarmauri_tts_gemini)](https://pepy.tech/projects/swarmauri_tts_gemini)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_gemini.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_gemini)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_gemini/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_gemini)](https://pypi.org/project/swarmauri_tts_gemini/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_gemini)](https://pypi.org/project/swarmauri_tts_gemini/)

## Features

- Synchronous/asynchronous file generation and bounded batches.
- Incremental HTTP audio with cancellation cleanup.
- Provider-specific authentication, payloads, formats and model validation.
- Fixed provider endpoints; no automatic replay of billable requests.

Unary output is WAV at 24 kHz mono; streaming decodes SSE audio events into headerless 16-bit little-endian PCM at 24 kHz. The API uses `store=false` and never stores a session ID locally. Set `TextToSpeechAgent.output_path` to a `.wav` filename.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_gemini
```

```bash
pip install --pre swarmauri_tts_gemini
```

This source candidate requires the companion `swarmauri_base>=0.11.0.dev9`
release before these alpha packages can be installed from the index.

## Usage

Set `GEMINI_API_KEY` privately. Use a model and voice available to your own account.

```python
import os
from swarmauri_tts_gemini import GeminiTTS

provider = GeminiTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    name="gemini-3.8-flash-tts",
    voice="Kore",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```

The filename does not convert the codec. Select matching output settings and
extensions. The component implements `TTSBase` for `TextToSpeechAgent` use.

## Models and output settings

The initial model list is `gemini-3.8-flash-tts` (default) and
`gemini-3.8-flash-lite-tts`, using the same Interactions schema. `voice`
defaults to `Kore`; optional `style` adds speech metadata to the text.
File generation always requests a complete WAV; streaming requests
`audio/l16`. Both use 24 kHz mono PCM16. Older model IDs using a different
API contract are rejected rather than sent to this endpoint.

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6298](https://github.com/swarmauri/swarmauri-sdk/issues/6298). No paid synthesis was run. Offline tests
cover transport and documented schemas, not account/model availability,
playability, latency, pricing or quality. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review sufficient live evidence.

Live tests require both `GEMINI_API_KEY` and `SWARMAURI_LIVE_TTS=1`.
Gemini defaults to `Kore`; select a permitted voice for other checks.
By default only `predict` runs (one request). Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
to select all operations (eight requests per model). Use
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` for model-specific checks.
Never paste keys into logs or issues. See the
[verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).

For speaker-labelled turns with explicit voice bindings, use the separate
swarmauri_tts_gemini_dialogue package. It reuses this package's audio decoding
while preserving a distinct structured input contract.
