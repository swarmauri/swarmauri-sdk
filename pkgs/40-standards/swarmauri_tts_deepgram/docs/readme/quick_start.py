import os
from swarmauri_tts_deepgram import DeepgramTTS

provider = DeepgramTTS(
    api_key=os.environ["DEEPGRAM_API_KEY"],
    name="aura-2-thalia-en",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
