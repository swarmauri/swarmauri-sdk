![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_azure

Alpha Swarmauri Azure Speech TTS provider. Public-cloud regional REST synthesis using a Speech resource key and escaped SSML. `name` is the voice ShortName, rather than a separate model ID.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_azure)](https://pepy.tech/projects/swarmauri_tts_azure)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_azure.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_azure)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_azure)](https://pypi.org/project/swarmauri_tts_azure/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_azure)](https://pypi.org/project/swarmauri_tts_azure/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_azure?label=swarmauri_tts_azure&color=green)](https://pypi.org/project/swarmauri_tts_azure/)

## Features

- File synthesis, asynchronous synthesis and bounded batches through TTSBase.
- Incremental HTTP audio with response cleanup on stream cancellation.
- Provider-specific authentication, encoding and region configuration.
- No automatic replay of billable synthesis requests.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_azure
```

```bash
pip install --pre swarmauri_tts_azure
```

Python 3.10-3.12. This source candidate requires the companion
`swarmauri_base>=0.11.0.dev10` release before index installation.

## Usage

```python
import os
from swarmauri_tts_azure import AzureTTS

provider = AzureTTS(
    api_key=os.environ["AZURE_SPEECH_KEY"],
    region=os.environ["AZURE_SPEECH_REGION"],
    name="en-US-JennyNeural",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```

Use the component with TextToSpeechAgent. Select a filename matching the output
format; HTTP chunks retain that codec. No realtime latency claim is made.

## Configuration and API scope

The initial voices are en-US-JennyNeural (default), en-US-AriaNeural and
en-US-GuyNeural, with `locale="en-US"`. The input is plain text: markup and XML
characters are escaped into a single SSML voice element. Invalid XML control
characters fail locally. Custom voice deployments, raw user-supplied SSML,
Entra/STS token acquisition, sovereign/private endpoints and batch/Long Audio
APIs are excluded. Regional stock-voice availability needs live verification.

`output_format` supports audio-24khz-48kbitrate-mono-mp3 (default),
riff-24khz-16bit-mono-pcm (WAV), raw-24khz-16bit-mono-pcm,
raw-8khz-8bit-mono-mulaw and ogg-24khz-16bit-mono-opus.
Raw PCM/mulaw have no container header. Filenames do not change codecs.
The REST service limits generated audio to ten minutes; this adapter does not
silently split long text. Event-driven Speech SDK features need another interface.

Primary reference: [Azure Speech synthesis API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech).

## Verification and alpha status

Live API behavior remains **unverified**; tracked in [#6302](https://github.com/swarmauri/swarmauri-sdk/issues/6302). No paid synthesis was run. Offline
contract tests do not establish account/model availability, output playability,
quality, latency or billed cost. Keep `Development Status :: 3 - Alpha` in
`pyproject.toml` until maintainers review sufficient live evidence.

The live suite requires explicit `SWARMAURI_LIVE_TTS=1` plus private AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.
A credential alone never enables it. Run the package's `tests/i9n` suite.
By default only predict runs (one billable request). Select additional operations
with `SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
(eight requests per model/voice because each batch has two inputs).
Set `SWARMAURI_TTS_MODEL` to the engine (Polly) or voice ShortName (Azure).
Azure does not use `SWARMAURI_TTS_VOICE`.
Never paste secrets or unmasked authorization headers in logs or issues.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
