![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_cartesia

Alpha Swarmauri Cartesia speech provider. Versioned Sonic bytes API. WebSockets, SSE and voice management are excluded.

[![Downloads](https://static.pepy.tech/badge/swarmauri_tts_cartesia)](https://pepy.tech/projects/swarmauri_tts_cartesia)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_cartesia.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_cartesia)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_cartesia/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_cartesia)](https://pypi.org/project/swarmauri_tts_cartesia/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_cartesia)](https://pypi.org/project/swarmauri_tts_cartesia/)

## Features

- Synchronous/asynchronous file generation and bounded batches.
- Incremental HTTP audio with cancellation cleanup.
- Provider-specific authentication, payloads, formats and model validation.
- Fixed provider endpoints; no automatic replay of billable requests.

`voice` must be an account-accessible voice ID. HTTP chunks retain the selected output codec. No realtime latency claim is made.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_cartesia
```

```bash
pip install --pre swarmauri_tts_cartesia
```

This source candidate requires the companion `swarmauri_base>=0.11.0.dev9`
release before these alpha packages can be installed from the index.

## Usage

Set `CARTESIA_API_KEY` privately. Use a model and voice available to your own account.

```python
import os
from swarmauri_tts_cartesia import CartesiaTTS

provider = CartesiaTTS(
    api_key=os.environ["CARTESIA_API_KEY"],
    name="sonic-3.6",
    voice="db6b0ed5-d5d3-463d-ae85-518a07d3c2b4",
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

The initial model list is `sonic-3.6`, `sonic-3.5` and `sonic-3`.
`api_version` is pinned to `2026-08-14`. Select `response_format="mp3"`
(default), `"wav"` or `"raw"`; WAV/raw use `pcm_s16le`. Set `sample_rate`
to 8000, 16000, 22050, 24000, 44100 (default) or 48000. `bit_rate` applies
only to MP3 (default 128000). Optional `speed` ranges from 0.6 to 1.5;
`language` passes the language code to Cartesia.

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6293](https://github.com/swarmauri/swarmauri-sdk/issues/6293). No paid synthesis was run. Offline tests
cover transport and documented schemas, not account/model availability,
playability, latency, pricing or quality. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review sufficient live evidence.

Live tests require both `CARTESIA_API_KEY` and `SWARMAURI_LIVE_TTS=1`.
An explicit `SWARMAURI_TTS_VOICE` is required.
By default only `predict` runs (one request). Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
to select all operations (eight requests per model). Use
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` for model-specific checks.
Never paste keys into logs or issues. See the
[verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
