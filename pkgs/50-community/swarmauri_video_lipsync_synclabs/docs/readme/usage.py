import os

from swarmauri_video_lipsync_synclabs import SyncLabsLipSync

lip_sync = SyncLabsLipSync(api_key=os.environ["SYNC_API_KEY"])
result = lip_sync.predict(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
    "dubbed.mp4",
    sync_mode="cut_off",
)
print(result)
