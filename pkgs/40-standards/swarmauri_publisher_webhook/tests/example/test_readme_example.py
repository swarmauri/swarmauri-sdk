"""Execute the usage example from the README to guard against regressions."""

from __future__ import annotations

import httpx
import pytest

from swarmauri_publisher_webhook import WebhookPublisher


@pytest.mark.example
def test_readme_usage_example(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the documented quickstart and assert the emitted payload."""

    recorded: dict[str, object] = {}

    def fake_post(
        self: httpx.Client,
        url: str,
        *,
        json: dict[str, object],
        **_: object,
    ) -> httpx.Response:  # type: ignore[override]
        recorded["url"] = url
        recorded["json"] = json
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.Client, "post", fake_post, raising=True)

    publisher = WebhookPublisher(url="https://your-webhook-endpoint.com/hook")

    publisher.publish(
        channel="my_data_stream",
        payload={"message": "Hello, webhook!", "value": 123},
    )

    assert recorded == {
        "url": "https://your-webhook-endpoint.com/hook",
        "json": {
            "channel": "my_data_stream",
            "payload": {"message": "Hello, webhook!", "value": 123},
        },
    }
