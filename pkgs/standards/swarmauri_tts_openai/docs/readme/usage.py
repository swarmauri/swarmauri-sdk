import os
from swarmauri_tts_openai import OpenaiTTS

provider = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="tts-1",
    voice="alloy",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
