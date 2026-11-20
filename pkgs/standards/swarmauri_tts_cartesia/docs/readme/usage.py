import os
from swarmauri_tts_cartesia import CartesiaTTS

provider = CartesiaTTS(
    api_key=os.environ["CARTESIA_API_KEY"],
    name="sonic-3.6",
    voice="db6b0ed5-d5d3-463d-ae85-518a07d3c2b4",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
