import pytest
from swarmauri_base.publishers.PublishBase import PublishBase


class DummyPublisher(PublishBase):
    def publish(self, channel: str, payload: dict) -> None:
        self.last = (channel, payload)


@pytest.mark.unit
def test_publish_base_defaults():
    pub = DummyPublisher()
    pub.publish("chan", {"a": 1})
    assert pub.resource == "Publisher"
    assert pub.type == "PublishBase"
    assert pub.last == ("chan", {"a": 1})
