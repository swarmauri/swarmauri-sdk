# Migrate from Play.ht

Play.ht's TTS service is discontinued. AudioStack confirmed its voices no longer
work in its [provider deprecation notice](https://docs.audiostack.ai/changelog/30th-july-2025-playht-deprecation-notice).

Both packages now live under `pkgs/deprecated/` and retain their distribution
and import names. `swarmauri_tts_playht` and `swarmauri_llm_playht` are deprecated and marked
inactive. The bundled `PlayhtTTS` and legacy LLM `PlayHTModel` are deprecated too.
Old imports and facade names remain available for compatibility, but construction
raises a local error before credentials are validated or a network request occurs.
The `swarmauri-playht` command reports the same migration guidance. The facade's
`llms` extra no longer installs Play.ht. No credentials are redirected to another
service, and no models or voice IDs are silently translated.

## Replacement choice

Use the existing `OpenaiTTS` for text-to-audio files, synchronous/asynchronous
execution, streaming and batches. It already implements `TTSBase` and works with
`TextToSpeechAgent`, so callers retain the same file-path contract.

| Option | Fit | Migration cost |
| --- | --- | --- |
| OpenAI `OpenaiTTS` | Existing Swarmauri provider; file, async, streaming and batch workflows | New API key, model and voice |
| ElevenLabs | Voice cloning and streaming APIs | A new Swarmauri adapter and separate voice provisioning |
| Cartesia | Realtime streaming TTS | A new Swarmauri adapter and separate voice provisioning |

This choice is based on integration coverage, not a quality, latency or price
benchmark. OpenAI is not a drop-in replacement for Play.ht voice management.
Voice cloning, listing and deletion require a separate provider-specific migration.
Re-provision voices using source recordings you are authorized to use; Play.ht
credentials, user IDs, voice names and clone IDs cannot be reused.

Provider references: [OpenAI speech guide](https://developers.openai.com/api/docs/guides/text-to-speech),
[ElevenLabs streaming](https://elevenlabs.io/docs/api-reference/text-to-speech/stream),
[Cartesia migration guide](https://www.cartesia.ai/migrate/playht).

## Install and configure

```bash
uv add swarmauri_standard
# Or:
pip install swarmauri_standard
```

Set `OPENAI_API_KEY` to a new OpenAI API key, then replace your provider:

```python
import os

from swarmauri_standard.tts.OpenaiTTS import OpenaiTTS

tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
audio_path = tts.predict("Welcome to Swarmauri.", "welcome.mp3")
# Async: await tts.apredict(text, audio_path)
# Streaming: tts.stream(text) or async iteration over tts.astream(text)
```

Pass this `tts` to `TextToSpeechAgent` without changing its execution methods.
Remove Play.ht dependencies and `PLAYHT_*` environment settings. For the realtime
voice showcase, use `GROQ_API_KEY`, `OPENAI_API_KEY`, `OPENAI_TTS_MODEL` and
`OPENAI_TTS_VOICE`; select `VOICE_PIPELINE=swarmauri` or `groq_openai`.

## Impact and release order

- SDK: both standalone packages, bundled implementations, facade aggregate
  dependencies, agent examples and retirement tests.
- `tigrbl/tigrbl_realtime_ws_agent2user`: provider, dependency, environment
  example, Compose configuration and setup instructions.
- `swarmauri/swarmauri-com`: package catalog generator and generated listings.
- `swarmauri/docs-swarmauri-com`: public provider navigation and overview.

Historical release records are retained. Publish the SDK deprecation releases,
then release consumers and regenerate/deploy the public documentation. Source
changes alone do not update already published PyPI releases or live deployments.
