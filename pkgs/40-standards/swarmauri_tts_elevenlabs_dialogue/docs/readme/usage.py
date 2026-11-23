import os
from swarmauri_tts_elevenlabs_dialogue import (
    ElevenLabsDialogueTTS,
    DialogueTurn,
)

provider = ElevenLabsDialogueTTS(api_key=os.environ["ELEVENLABS_API_KEY"])
turns = (
    DialogueTurn(text="[curious] Hello?", voice_id=os.environ["VOICE_ONE"]),
    DialogueTurn(text="Hello back!", voice_id=os.environ["VOICE_TWO"]),
)
path = provider.predict(turns, "dialogue.mp3")
# await provider.apredict(turns, "dialogue.mp3")
# provider.batch({turns: "dialogue.mp3"})
# await provider.abatch({turns: "dialogue.mp3"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
