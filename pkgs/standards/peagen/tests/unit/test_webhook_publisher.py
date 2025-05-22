from unittest.mock import MagicMock, patch

import pytest
import httpx

from peagen.publishers.webhook_publisher import WebhookPublisher


@pytest.mark.unit
def test_success():
    resp = MagicMock(status_code=200)
    with patch("httpx.post", return_value=resp) as mock_post:
        pub = WebhookPublisher("https://example.com")
        pub.publish("chan", {"x": 1})
        mock_post.assert_called_once_with(
            "https://example.com", json={"channel": "chan", "payload": {"x": 1}}
        )


@pytest.mark.unit
def test_http_error():
    with patch("httpx.post", side_effect=httpx.HTTPError("boom")):
        pub = WebhookPublisher("https://example.com")
        with pytest.raises(RuntimeError):
            pub.publish("chan", {})


@pytest.mark.unit
def test_non_200():
    resp = MagicMock(status_code=500, text="fail")
    with patch("httpx.post", return_value=resp):
        pub = WebhookPublisher("https://example.com")
        with pytest.raises(RuntimeError):
            pub.publish("chan", {})

