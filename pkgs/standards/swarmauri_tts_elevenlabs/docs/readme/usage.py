import os
from swarmauri_tts_elevenlabs import ElevenLabsTTS

provider = ElevenLabsTTS(
    api_key=os.environ["ELEVENLABS_API_KEY"],
    name="eleven_multilingual_v2",
    voice="JBFqnCBsd6RMkjVDRZzb",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
