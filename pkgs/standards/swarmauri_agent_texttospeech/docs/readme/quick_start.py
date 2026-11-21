import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_openai import OpenaiTTS

tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
agent = TextToSpeechAgent(tts=tts, output_path="greeting.mp3")

audio_path = agent.exec("Welcome to Swarmauri.")
print(audio_path)
