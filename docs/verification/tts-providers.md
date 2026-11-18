# Alpha TTS provider verification

OpenAI is `0.1.0a2`; the other thirteen packages are `0.1.0a1`. All retain
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
| `swarmauri_tts_polly.PollyTTS` | Unverified | [#6301](https://github.com/swarmauri/swarmauri-sdk/issues/6301) |
| `swarmauri_tts_azure.AzureTTS` | Unverified | [#6302](https://github.com/swarmauri/swarmauri-sdk/issues/6302) |
| `swarmauri_tts_elevenlabs_dialogue.ElevenLabsDialogueTTS` | Unverified | [#6304](https://github.com/swarmauri/swarmauri-sdk/issues/6304) |
| `swarmauri_tts_gemini_dialogue.GeminiDialogueTTS` | Unverified | [#6308](https://github.com/swarmauri/swarmauri-sdk/issues/6308) |
| `swarmauri_tts_deepinfra_kokoro.DeepInfraKokoroTTS` | Unverified | [#6305](https://github.com/swarmauri/swarmauri-sdk/issues/6305) |
| `swarmauri_tts_deepinfra_qwen3.DeepInfraQwen3TTS` | Unverified | [#6306](https://github.com/swarmauri/swarmauri-sdk/issues/6306) |
| `swarmauri_tts_deepinfra_qwen3_voicedesign.DeepInfraQwen3VoiceDesignTTS` | Unverified | [#6307](https://github.com/swarmauri/swarmauri-sdk/issues/6307) |

## Run a verification

Use your own authorized account and set its credential locally:
`OPENAI_API_KEY`, `DEEPINFRA_API_KEY`, `TOGETHER_API_KEY`, `CARTESIA_API_KEY`,
`ELEVENLABS_API_KEY`, `DEEPGRAM_API_KEY` or `GEMINI_API_KEY`. A key alone never
enables these live tests. Explicitly set `SWARMAURI_LIVE_TTS=1` to authorize
billable requests, then run the selected package's `tests/i9n` suite.
Polly instead requires explicit `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_REGION` and, for temporary credentials, `AWS_SESSION_TOKEN`. Azure requires
`AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`. Credentials alone never opt in:

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
the voice in the model ID. Gemini defaults to Kore. For Polly,
`SWARMAURI_TTS_MODEL` is the engine and `SWARMAURI_TTS_VOICE` is a compatible
voice. For Azure, `SWARMAURI_TTS_MODEL` is the voice ShortName; the separate
voice variable is unused. The live harness uses default MP3 for these two;
other formats require explicit component configuration in a local script. Do not
paste keys or unmasked authorization headers into issues, logs or fixtures.

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
- DeepInfra uses `https://api.deepinfra.com/v1/openai/audio/speech`, not the native
  `/v1/inference/{model}` route. Confirm that each listed catalog model works
  through this endpoint and returns binary audio; the current Kokoro model
  example documents this route and binary output. A native-only model needs
  a separate adapter/interface.
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

- Polly uses SigV4-signed UTF-8 JSON on regional `/v1/speech` endpoints.
  `name` is the engine; `voice` is a compatible voice ID. Credentials are explicit,
  including session tokens where applicable; there is no profile/IMDS lookup or
  automatic credential refresh. Only commercial AWS regions and plain text are
  supported. Speech marks, SSML and S3 synthesis jobs have different contracts.
- Azure uses the public regional Speech REST endpoint, resource-key auth and
  escaped SSML. `name` is a stock voice ShortName. MP3, WAV, raw PCM/mulaw and
  Ogg/Opus are exposed through an output-format header. Custom voices, sovereign
  endpoints, token acquisition and batch/Long Audio APIs are excluded. The REST
  API truncates generated audio at ten minutes; no automatic splitting is done.

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
Priority-two and priority-three interfaces were checked on 2026-11-18;
live behavior remains unverified. Priority-three references:
[Polly SynthesizeSpeech](https://docs.aws.amazon.com/polly/latest/APIReference/API_SynthesizeSpeech.html),
[botocore SigV4 signer](https://github.com/boto/botocore/blob/develop/botocore/auth.py),
[Azure Speech REST](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech).

## Interface-specific adapters

See [interface boundaries](../research/tts-interface-boundaries.md) for the
split between native Kokoro, native Qwen3 presets, Qwen3 voice descriptions and
ElevenLabs ordered dialogue. The DeepInfra native packages decode complete JSON
responses; stream/astream are intentionally unsupported and raise locally.
Their four supported operations make six calls when all are selected. Their
live suites collect but skip the two unsupported streaming operations even
when opted in. The ElevenLabs dialogue suite needs two account-accessible IDs
in SWARMAURI_TTS_VOICE and SWARMAURI_TTS_SECOND_VOICE; all six operations make
eight calls. Gemini dialogue uses speaker-labelled turns with two voice bindings;
its six-operation suite also makes eight calls and defaults to Puck/Kore.
Its file output is WAV and streams are raw PCM24k. Voice design requires SWARMAURI_TTS_VOICE_DESCRIPTION. The native
suites default to WAV, and the dialogue suite defaults to MP3. Default selection
remains predict only (one call).

## Compatibility and release order

The new packages depend on `swarmauri_base` for the HTTP transport mixin and do
not depend on `swarmauri_standard`. The standard and community OpenAI packages
preserve legacy imports through warning shims. The facade exposes canonical
TTS classes and has a separate `tts` installation extra. The new five packages
remain alpha and do not replace any existing import path.

Release `swarmauri_base>=0.11.0.dev12` first, then the fourteen alpha packages,
followed by the updated standard/community/facade distributions. Building and
testing this source candidate does not publish these versions to PyPI.

## Existing provider lifecycle

OpenAI Speech models remain live-unverified here and are scheduled to shut down
on 2027-01-06. #6268 is not a promotion path around that lifecycle; track the
separate Realtime migration in [#6310](https://github.com/swarmauri/swarmauri-sdk/issues/6310).
See [the lifecycle guide](../migrations/openai-speech.md).
HyperbolicTTS and HyperbolicAudioTTS now fail locally because their old endpoint
was decommissioned; no paid verification should be attempted against that route.
