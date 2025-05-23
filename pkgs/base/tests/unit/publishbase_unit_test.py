"""Unit tests for ``PublishBase`` implementations."""

import pytest
from swarmauri_base.publishers.PublishBase import PublishBase


class DummyPublisher(PublishBase):
    """Minimal publisher used in tests."""

    def publish(self, channel: str, payload: dict) -> None:
        """Record the published channel and payload."""
        self.last = (channel, payload)


@pytest.mark.unit
def test_publish_base_defaults():
    """Ensure defaults and publish behavior are correct."""
    pub = DummyPublisher()
    pub.publish("chan", {"a": 1})
    assert pub.resource == "Publisher"
    assert pub.type == "DummyPublisher"
    assert pub.last == ("chan", {"a": 1})
