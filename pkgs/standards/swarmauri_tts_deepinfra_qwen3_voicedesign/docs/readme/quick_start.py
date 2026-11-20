import os
from swarmauri_tts_deepinfra_qwen3_voicedesign import (
    DeepInfraQwen3VoiceDesignTTS,
)

provider = DeepInfraQwen3VoiceDesignTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    voice_description="A calm, warm narrator with a low voice",
    language="English",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
