import os
from swarmauri_tts_azure import AzureTTS

provider = AzureTTS(
    api_key=os.environ["AZURE_SPEECH_KEY"],
    region=os.environ["AZURE_SPEECH_REGION"],
    name="en-US-JennyNeural",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
