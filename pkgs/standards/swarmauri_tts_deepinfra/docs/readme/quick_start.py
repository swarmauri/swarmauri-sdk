import os
from swarmauri_tts_deepinfra import DeepInfraTTS

provider = DeepInfraTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="hexgrad/Kokoro-82M",
    voice="af_heart",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
