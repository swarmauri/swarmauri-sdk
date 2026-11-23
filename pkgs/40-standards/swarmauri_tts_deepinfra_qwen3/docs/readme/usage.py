import os
from swarmauri_tts_deepinfra_qwen3 import DeepInfraQwen3TTS

provider = DeepInfraQwen3TTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    voice="Vivian",
    language="English",
    instruct="Calm and clear",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
