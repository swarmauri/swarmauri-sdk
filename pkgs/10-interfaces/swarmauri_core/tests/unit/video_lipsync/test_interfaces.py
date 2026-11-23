"""Tests for lip-sync interface contracts and event typing."""

from inspect import isabstract

from swarmauri_core.video_lipsync import (
    ILipSync,
    IQueuedLipSync,
    LipSyncJobEvent,
)


def test_lipsync_interfaces_are_abstract() -> None:
    assert isabstract(ILipSync)
    assert isabstract(IQueuedLipSync)


def test_job_event_is_a_lightweight_mapping() -> None:
    event = LipSyncJobEvent(
        job_id="job-1",
        status="RUNNING",
        progress=0.5,
    )

    assert event == {
        "job_id": "job-1",
        "status": "RUNNING",
        "progress": 0.5,
    }
