"""Shared lightweight typing definitions for lip-sync jobs."""

from typing import Literal, TypedDict


LipSyncJobStatus = Literal[
    "QUEUED",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "REJECTED",
]


class LipSyncJobEvent(TypedDict, total=False):
    """Normalized state emitted by a queued lip-sync provider."""

    job_id: str
    status: LipSyncJobStatus
    progress: float
    message: str
    output_url: str
    error_code: str
