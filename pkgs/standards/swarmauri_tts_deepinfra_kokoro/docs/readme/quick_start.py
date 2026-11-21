import os
from swarmauri_tts_deepinfra_kokoro import DeepInfraKokoroTTS

provider = DeepInfraKokoroTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    preset_voices=["af_bella", "af_heart"],
    speed=1.0,
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
