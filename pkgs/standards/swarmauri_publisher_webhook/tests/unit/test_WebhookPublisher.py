from unittest.mock import MagicMock, patch

import httpx
import pytest
from swarmauri_publisher_webhook.WebhookPublisher import WebhookPublisher


@pytest.fixture
def webhook_url() -> str:
    return "https://example.com/test-hook"


@pytest.fixture
def publisher(webhook_url: str) -> WebhookPublisher:
    return WebhookPublisher(url=webhook_url)


@pytest.mark.unit
def test_ubc_resource(publisher):
    assert publisher.resource == "Publisher"


@pytest.mark.unit
def test_ubc_type(publisher):
    assert publisher.type == "WebhookPublisher"


@pytest.mark.unit
def test_webhookpublisher_initialization_invalid_url():
    with pytest.raises(ValueError):
        WebhookPublisher(url="not_a_valid_url")


@pytest.mark.unit
def test_publish_success(
    publisher: WebhookPublisher,
    webhook_url: str,  # mock_httpx_post is no longer injected here
):
    # Patch the 'post' method of the publisher's internal httpx.Client instance
    with patch.object(publisher._client, "post") as mock_client_post:
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.text = "Success"
        # Configure raise_for_status on the mock_response itself, as it would be on a real response
        mock_response.raise_for_status = MagicMock()
        mock_client_post.return_value = mock_response

        channel = "test_channel"
        payload = {"key": "value", "num": 123}
        expected_json_body = {"channel": channel, "payload": payload}

        publisher.publish(channel, payload)

        mock_client_post.assert_called_once_with(
            str(webhook_url), json=expected_json_body
        )
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.unit
# Remove the old @patch("httpx.post")
def test_publish_http_error(
    publisher: WebhookPublisher,
):  # mock_httpx_post is no longer injected here
    # Patch the 'post' method of the publisher's internal httpx.Client instance
    with patch.object(publisher._client, "post") as mock_client_post:
        mock_client_post.side_effect = httpx.RequestError("Network error")

        with pytest.raises(
            RuntimeError,
            match="Failed to POST to https://example.com/test-hook: Network error",
        ):
            publisher.publish("test_channel", {"key": "value"})
