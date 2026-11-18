# Alpha TTS provider verification

All seven packages start at `0.1.0a1` and retain
`Development Status :: 3 - Alpha` in their `pyproject.toml` and wheel metadata.
They were implemented against public API documentation and tested offline.
No live synthesis, speech-quality evaluation or paid provider request was run.

| Package/component | Live status | Verification issue |
| --- | --- | --- |
| `swarmauri_tts_openai.OpenaiTTS` | Unverified | [#6268](https://github.com/swarmauri/swarmauri-sdk/issues/6268) |
| `swarmauri_tts_deepinfra.DeepInfraTTS` | Unverified | [#6269](https://github.com/swarmauri/swarmauri-sdk/issues/6269) |
| `swarmauri_tts_together.TogetherTTS` | Unverified | [#6270](https://github.com/swarmauri/swarmauri-sdk/issues/6270) |
| `swarmauri_tts_cartesia.CartesiaTTS` | Unverified | [#6293](https://github.com/swarmauri/swarmauri-sdk/issues/6293) |
| `swarmauri_tts_elevenlabs.ElevenLabsTTS` | Unverified | [#6295](https://github.com/swarmauri/swarmauri-sdk/issues/6295) |
| `swarmauri_tts_deepgram.DeepgramTTS` | Unverified | [#6296](https://github.com/swarmauri/swarmauri-sdk/issues/6296) |
| `swarmauri_tts_gemini.GeminiTTS` | Unverified | [#6298](https://github.com/swarmauri/swarmauri-sdk/issues/6298) |

## Run a verification

Use your own authorized account and set its credential locally:
`OPENAI_API_KEY`, `DEEPINFRA_API_KEY`, `TOGETHER_API_KEY`, `CARTESIA_API_KEY`,
`ELEVENLABS_API_KEY`, `DEEPGRAM_API_KEY` or `GEMINI_API_KEY`. A key alone never
enables these live tests. Explicitly set `SWARMAURI_LIVE_TTS=1` to authorize
billable requests, then run the selected package's `tests/i9n` suite:

```bash
uv run --directory pkgs/standards/swarmauri_tts_openai \
  --package swarmauri_tts_openai pytest tests/i9n -q
```

By default only `predict` executes, making one synthesis request. The other
operations are collected but skipped. Set `SWARMAURI_LIVE_TTS_OPERATIONS` to a
comma-separated selection of `predict,apredict,stream,astream,batch,abatch` to
authorize additional calls. All six operations together generate eight requests
per model because each batch has two inputs. No automatic retry is performed.

Use `SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` to select each documented
model/voice. Kokoro voices differ from Orpheus or Chatterbox voices. Do not assume
one provider's voices or credentials transfer to another. Cartesia and ElevenLabs
require an explicit account-accessible `SWARMAURI_TTS_VOICE`; Deepgram embeds
the voice in the model ID. Gemini defaults to Kore. Do not paste keys or
unmasked authorization headers into issues, logs or fixtures.

Record the commit/package version, model, voice, operation, format/sample rate,
date and sanitized outcome in the linked issue. Check playable file output,
actual incremental delivery, async/batch behavior and cancellation cleanup.
Label every untested model/operation explicitly. A successful mocked test, one
live model or one operation does not establish verification of the full package.
Keep the alpha classifier until maintainers review sufficient live evidence.

## API boundaries and limits

- OpenAI uses binary audio from `/v1/audio/speech`. The legacy standard and
  LLM-named imports warn and delegate to the new package; the legacy
  `OpenAIAudioTTS` class retains its `type`, LLM resource and timeout default.
- DeepInfra uses `https://api.deepinfra.com/v1/audio/speech`, not the native
  `/v1/inference/{model}` route. Confirm that each listed catalog model works
  through this endpoint and returns binary audio; its reference schema labels
  the response JSON. A native-only model needs a separate adapter/interface.
  HTTP chunk iteration is implemented, but no realtime latency claim is made.
- Together file generation uses binary MP3, WAV or raw audio. Streaming sends
  `stream=true` and `response_format=raw`, decodes base64 audio SSE events and
  returns PCM bytes, at the configured sample rate (default 24000 Hz) with
  `pcm_s16le` encoding. Missing `[DONE]`, malformed audio and provider error
  events are reported as errors. WebSocket sessions are outside this package.
- Cartesia uses the versioned `/tts/bytes` API with Bearer authentication and
  `Cartesia-Version: 2026-08-14`. Sonic 3.6/3.5/3 share this interface. MP3,
  WAV and raw PCM output retain their configured codec in HTTP chunks.
- ElevenLabs uses `xi-api-key`, a voice-specific URL, and a distinct `/stream`
  suffix. The initial model list is Multilingual v2 and Flash v2.5, with MP3,
  PCM24k and mulaw8k formats. Text-to-Dialogue is a different API and excluded.
- Deepgram Aura REST uses Token authentication and model/encoding query
  parameters on `/v1/speak`. The voice is part of the model ID. Output settings
  are validated by encoding; MP3 has no sample-rate/container override. Flux
  and WebSocket sessions are outside this adapter.
- Gemini uses the Gemini 3.8 Interactions speech contract. Unary responses
  decode the last model-output audio block from JSON to a complete WAV file;
  streams decode `step.delta` SSE audio and require `interaction.completed`.
  Streaming bytes are headerless pcm_s16le, 24 kHz, mono. `store=false` keeps
  requests stateless. Older generateContent, multi-speaker, voice creation and
  Gemini Live contracts need distinct interfaces and are excluded.

Sources: [OpenAI speech API](https://developers.openai.com/api/reference/resources/audio/subresources/speech/methods/create),
[DeepInfra speech API](https://docs.deepinfra.com/api-reference/audio/openai-audio-speech),
[Together streaming](https://docs.together.ai/docs/inference/text-to-speech/streaming),
[Cartesia bytes](https://docs.cartesia.ai/api-reference/tts/bytes),
[ElevenLabs convert](https://elevenlabs.io/docs/api-reference/text-to-speech/convert),
[ElevenLabs stream](https://elevenlabs.io/docs/api-reference/text-to-speech/stream),
[Deepgram speak](https://developers.deepgram.com/reference/text-to-speech/speak-request),
[Deepgram output settings](https://developers.deepgram.com/docs/tts-media-output-settings),
[Gemini speech](https://aistudio.google.com/docs/speech-generation),
[Gemini streaming](https://ai.google.dev/gemini-api/docs/streaming).
The priority-two interfaces were checked on 2026-11-18; live behavior remains unverified.

## Compatibility and release order

The new packages depend on `swarmauri_base` for the HTTP transport mixin and do
not depend on `swarmauri_standard`. The standard and community OpenAI packages
preserve legacy imports through warning shims. The facade exposes canonical
TTS classes and has a separate `tts` installation extra.

Release `swarmauri_base>=0.11.0.dev9` first, then the seven alpha providers,
followed by the updated standard/community/facade distributions. Building and
testing this source candidate does not publish these versions to PyPI.
