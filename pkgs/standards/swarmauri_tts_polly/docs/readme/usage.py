import os
from swarmauri_tts_polly import PollyTTS

provider = PollyTTS(
    access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    session_token=os.getenv("AWS_SESSION_TOKEN"),
    region=os.environ["AWS_REGION"],
    name="neural",
    voice="Joanna",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.mp3"})
# await provider.abatch({"Hello": "hello.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
