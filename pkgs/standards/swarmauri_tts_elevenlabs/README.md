![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_elevenlabs

Alpha Swarmauri ElevenLabs speech provider. Single-speaker speech and stream endpoints for Multilingual v2 and Flash v2.5. Dialogue, v4/Turbo dialogue interfaces, WebSockets and cloning are excluded.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_elevenlabs)](https://pepy.tech/projects/swarmauri_tts_elevenlabs)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_elevenlabs.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_elevenlabs)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_elevenlabs)](https://pypi.org/project/swarmauri_tts_elevenlabs/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_elevenlabs)](https://pypi.org/project/swarmauri_tts_elevenlabs/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_elevenlabs?label=swarmauri_tts_elevenlabs&color=green)](https://pypi.org/project/swarmauri_tts_elevenlabs/)

## Features

- Synchronous/asynchronous file generation and bounded batches.
- Incremental HTTP audio with cancellation cleanup.
- Provider-specific authentication, payloads, formats and model validation.
- Fixed provider endpoints; no automatic replay of billable requests.

`voice` must be an account-accessible voice ID. HTTP chunks retain the selected output codec. No realtime latency claim is made.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_elevenlabs
```

```bash
pip install --pre swarmauri_tts_elevenlabs
```

This source candidate requires the companion `swarmauri_base>=0.11.0.dev12`
release before these alpha packages can be installed from the index.

## Usage

Set `ELEVENLABS_API_KEY` privately. Use a model and voice available to your own account.

```python
import os
from swarmauri_tts_elevenlabs import ElevenLabsTTS

provider = ElevenLabsTTS(
    api_key=os.environ["ELEVENLABS_API_KEY"],
    name="eleven_multilingual_v2",
    voice="JBFqnCBsd6RMkjVDRZzb",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```

The filename does not convert the codec. Select matching output settings and
extensions. The component implements `TTSBase` for `TextToSpeechAgent` use.

## Models and output settings

The initial model list is `eleven_multilingual_v2` (default) and
`eleven_flash_v2_5`. Use `output_format="mp3_44100_128"` (default),
`"pcm_24000"` or `"ulaw_8000"`. PCM and mulaw output are headerless;
select a matching extension and playback configuration. Account tiers can
restrict formats. Optional `stability` and `similarity_boost` each range
from 0 to 1. The `voice` ID selects both unary and streaming URLs.

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6295](https://github.com/swarmauri/swarmauri-sdk/issues/6295). No paid synthesis was run. Offline tests
cover transport and documented schemas, not account/model availability,
playability, latency, pricing or quality. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review sufficient live evidence.

Live tests require both `ELEVENLABS_API_KEY` and `SWARMAURI_LIVE_TTS=1`.
An explicit `SWARMAURI_TTS_VOICE` is required.
By default only `predict` runs (one request). Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
to select all operations (eight requests per model). Use
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` for model-specific checks.
Never paste keys into logs or issues. See the
[verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
