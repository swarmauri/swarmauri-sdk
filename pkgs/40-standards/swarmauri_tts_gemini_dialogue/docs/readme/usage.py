import os
from swarmauri_tts_gemini_dialogue import GeminiDialogueTTS, GeminiDialogueTurn

provider = GeminiDialogueTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    speaker_voices={"Joe": "Puck", "Jane": "Kore"},
)
turns = (
    GeminiDialogueTurn(text="How are you?", speaker="Joe", style="cheerful"),
    GeminiDialogueTurn(text="Doing well!", speaker="Jane"),
)
path = provider.predict(turns, "dialogue.wav")
# await provider.apredict(turns, "dialogue.wav")
# provider.batch({turns: "dialogue.wav"})
# await provider.abatch({turns: "dialogue.wav"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
