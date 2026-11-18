# OpenAI Speech API lifecycle

Checked against [OpenAI's deprecation schedule](https://developers.openai.com/api/docs/deprecations)
and [Speech guide](https://developers.openai.com/api/docs/guides/text-to-speech)
on 2026-11-18. tts-1, tts-1-hd and gpt-4o-mini-tts are deprecated and scheduled
to shut down on 2027-01-06. Existing Speech API integrations may continue their
current contract before shutdown; this is not a long-term replacement choice.

swarmauri_tts_openai remains an alpha compatibility adapter. It emits a
FutureWarning when preparing a speech request. Defaults, allowed legacy models,
MP3 behavior and deprecated import aliases are preserved. It does not silently
switch models or API families and does not promote live verification status.

OpenAI recommends gpt-realtime-2.1-mini through the Realtime API. That model is
not accepted by /v1/audio/speech. A Realtime integration needs an explicit
session/event contract and codec handling; it is not implemented by replacing
the name in OpenaiTTS. Track the migration in the repository's lifecycle issue.

For another existing alpha adapter, see the [provider inventory](../research/tts-provider-options.md)
and [verification issues](../verification/tts-providers.md). Verify account/model
availability and audio output with an explicitly authorized key before using a
provider in production. No paid synthesis was run for this update.

Migration tracking: [#6310](https://github.com/swarmauri/swarmauri-sdk/issues/6310).
