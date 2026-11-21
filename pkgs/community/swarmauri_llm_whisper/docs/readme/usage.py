import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test.mp3", task="transcription")

print(text)
