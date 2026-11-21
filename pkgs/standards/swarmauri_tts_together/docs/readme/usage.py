import os
from swarmauri_tts_together import TogetherTTS

provider = TogetherTTS(
    api_key=os.environ["TOGETHER_API_KEY"],
    name="canopylabs/orpheus-3b-0.1-ft",
    voice="tara",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
