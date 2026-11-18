![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_polly

Alpha Swarmauri Amazon Polly TTS provider. AWS Signature V4 signing with explicit credentials. `name` selects an engine (`standard`, `neural`, `long-form`, `generative`); `voice` selects a compatible voice ID. Engine/voice/region availability must be verified with your account.

[![Downloads](https://static.pepy.tech/badge/swarmauri_tts_polly)](https://pepy.tech/projects/swarmauri_tts_polly)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_polly.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_polly)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_polly/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_polly)](https://pypi.org/project/swarmauri_tts_polly/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_polly)](https://pypi.org/project/swarmauri_tts_polly/)

## Features

- File synthesis, asynchronous synthesis and bounded batches through TTSBase.
- Incremental HTTP audio with response cleanup on stream cancellation.
- Provider-specific authentication, encoding and region configuration.
- No automatic replay of billable synthesis requests.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_polly
```

```bash
pip install --pre swarmauri_tts_polly
```

Python 3.10-3.12. This source candidate requires the companion
`swarmauri_base>=0.11.0.dev10` release before index installation.

## Usage

```python
import os
from swarmauri_tts_polly import PollyTTS

provider = PollyTTS(
    access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    session_token=os.getenv("AWS_SESSION_TOKEN"),
    region=os.environ["AWS_REGION"],
    name="neural", voice="Joanna",
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

`response_format` supports MP3 (default), ogg_vorbis, ogg_opus, PCM, mulaw
and alaw. `sample_rate` is optional: MP3/Vorbis accept 8000, 16000, 22050,
24000, 44100 or 48000; Opus accepts 48000; PCM accepts 8000 or 16000;
mulaw/alaw accept 8000. PCM is headerless signed 16-bit little-endian mono.
Sample rates are sent as strings. Optional `language_code` selects the language
for bilingual voices. Filenames do not change codecs.

Credentials are explicit SecretStr fields and are never discovered from profiles,
metadata endpoints or the environment implicitly. The example reads environment
variables in the application. Supply a session token with temporary credentials
and replace the component when credentials expire; automatic role assumption or
credential refresh is not implemented. Commercial AWS region endpoints only;
China, GovCloud, FIPS and custom endpoints are excluded. Plain text only;
SSML, speech marks, voice discovery, lexicons and S3 synthesis jobs are excluded.
Polly limits plain-text requests to 3000 billed characters; no automatic text
splitting is performed.

Primary reference: [Amazon Polly synthesis API](https://docs.aws.amazon.com/polly/latest/APIReference/API_SynthesizeSpeech.html).

## Verification and alpha status

Live API behavior remains **unverified**; tracked in [#6301](https://github.com/swarmauri/swarmauri-sdk/issues/6301). No paid synthesis was run. Offline
contract tests do not establish account/model availability, output playability,
quality, latency or billed cost. Keep `Development Status :: 3 - Alpha` in
`pyproject.toml` until maintainers review sufficient live evidence.

The live suite requires explicit `SWARMAURI_LIVE_TTS=1` plus private AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_REGION; AWS_SESSION_TOKEN for temporary credentials.
A credential alone never enables it. Run the package's `tests/i9n` suite.
By default only predict runs (one billable request). Select additional operations
with `SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch`
(eight requests per model/voice because each batch has two inputs).
Set `SWARMAURI_TTS_MODEL` to the engine (Polly) or voice ShortName (Azure).
Use `SWARMAURI_TTS_VOICE` to select an engine-compatible voice.
Never paste secrets or unmasked authorization headers in logs or issues.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
