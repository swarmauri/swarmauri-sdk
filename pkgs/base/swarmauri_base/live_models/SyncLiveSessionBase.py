"""Sync façade marker for live sessions."""

from .LiveSessionBase import LiveSessionBase


class SyncLiveSessionBase(LiveSessionBase):
    """LiveSessionBase already supplies deterministic sync façades."""
