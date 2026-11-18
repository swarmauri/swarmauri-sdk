# Alpha TTS provider verification

All three packages start at `0.1.0a1` and retain
`Development Status :: 3 - Alpha` in their `pyproject.toml` and wheel metadata.
They were implemented against public API documentation and tested offline.
No live synthesis, speech-quality evaluation or paid provider request was run.

| Package/component | Live status | Verification issue |
| --- | --- | --- |
| `swarmauri_tts_openai.OpenaiTTS` | Unverified | [#6268](https://github.com/swarmauri/swarmauri-sdk/issues/6268) |
| `swarmauri_tts_deepinfra.DeepInfraTTS` | Unverified | [#6269](https://github.com/swarmauri/swarmauri-sdk/issues/6269) |
| `swarmauri_tts_together.TogetherTTS` | Unverified | [#6270](https://github.com/swarmauri/swarmauri-sdk/issues/6270) |

## Run a verification

Use your own authorized account and set its credential locally:
`OPENAI_API_KEY`, `DEEPINFRA_API_KEY` or `TOGETHER_API_KEY`. A key alone never
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
one provider's voices or credentials transfer to another. Do not paste keys or
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

Sources: [OpenAI speech API](https://developers.openai.com/api/reference/resources/audio/subresources/speech/methods/create),
[DeepInfra speech API](https://docs.deepinfra.com/api-reference/audio/openai-audio-speech),
[Together streaming](https://docs.together.ai/docs/inference/text-to-speech/streaming).

## Compatibility and release order

The new packages depend on `swarmauri_base` for the HTTP transport mixin and do
not depend on `swarmauri_standard`. The standard and community OpenAI packages
preserve legacy imports through warning shims. The facade exposes canonical
TTS classes and has a separate `tts` installation extra.

Release `swarmauri_base>=0.11.0.dev8` first, then the three alpha providers,
followed by the updated standard/community/facade distributions. Building and
testing this source candidate does not publish these versions to PyPI.
