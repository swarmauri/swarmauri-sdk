![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_deepgram

Alpha Swarmauri Deepgram speech provider. Aura REST /v1/speak. The voice is part of the model ID. Flux v2 and WebSocket sessions are excluded.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_deepgram)](https://pepy.tech/projects/swarmauri_tts_deepgram)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepgram.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepgram)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_deepgram)](https://pypi.org/project/swarmauri_tts_deepgram/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_deepgram)](https://pypi.org/project/swarmauri_tts_deepgram/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_deepgram?label=swarmauri_tts_deepgram&color=green)](https://pypi.org/project/swarmauri_tts_deepgram/)

## Features

- Synchronous/asynchronous file generation and bounded batches.
- Incremental HTTP audio with cancellation cleanup.
- Provider-specific authentication, payloads, formats and model validation.
- Fixed provider endpoints; no automatic replay of billable requests.

Use an Aura voice-model ID as `name`; there is no separate `voice` parameter. HTTP chunk streaming uses the REST API, not the WebSocket/Flux interface.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_deepgram
```

```bash
pip install --pre swarmauri_tts_deepgram
```

This source candidate requires the companion `swarmauri_base>=0.11.0.dev9`
release before these alpha packages can be installed from the index.

## Usage

Set `DEEPGRAM_API_KEY` privately. Use a model and voice available to your own account.

```python
import os
from swarmauri_tts_deepgram import DeepgramTTS

provider = DeepgramTTS(
    api_key=os.environ["DEEPGRAM_API_KEY"],
    name="aura-2-thalia-en",
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

The initial model list is `aura-2-thalia-en` (default),
`aura-2-andromeda-en` and `aura-2-selena-es`. MP3 is the default encoding
and has no sample-rate or container override. For WAV output, select
`encoding="linear16"` and optionally `sample_rate=24000`; the default
container is WAV. Use `container="none"` for headerless PCM. FLAC accepts
its documented sample rates and no container. `mulaw`/`alaw` accept
8000 or 16000 Hz with WAV or no container. Invalid combinations fail locally.

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6296](https://github.com/swarmauri/swarmauri-sdk/issues/6296). No paid synthesis was run. Offline tests
cover transport and documented schemas, not account/model availability,
playability, latency, pricing or quality. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review sufficient live evidence.

Live tests require both `DEEPGRAM_API_KEY` and `SWARMAURI_LIVE_TTS=1`.
Deepgram selects its voice through `SWARMAURI_TTS_MODEL`.
By default only `predict` runs (one request). Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
to select all operations (eight requests per model). Use
`SWARMAURI_TTS_MODEL` for voice-model-specific checks.
Never paste keys into logs or issues. See the
[verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
