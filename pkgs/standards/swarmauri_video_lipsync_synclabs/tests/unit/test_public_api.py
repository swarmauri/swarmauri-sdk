"""Tests for package exports."""

from swarmauri_video_lipsync_synclabs import SyncLabsLipSync


def test_public_export() -> None:
    assert SyncLabsLipSync.__name__ == "SyncLabsLipSync"
