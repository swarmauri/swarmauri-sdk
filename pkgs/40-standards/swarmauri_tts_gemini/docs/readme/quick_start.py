import os
from swarmauri_tts_gemini import GeminiTTS

provider = GeminiTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    name="gemini-3.8-flash-tts",
    voice="Kore",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
