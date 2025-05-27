from __future__ import annotations

from typing import Any, Dict

import httpx
from pydantic import Field, HttpUrl, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.publishers.PublishBase import PublishBase


@ComponentBase.register_model()
class WebhookPublisher(PublishBase):
    """
    Send JSON events to an HTTP endpoint.
    Inherits from PublishBase.
    """

    url: HttpUrl = Field(..., description="The URL of the webhook endpoint.")

    _client: httpx.Client = PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._client = httpx.Client()

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """
        POST ``payload`` to the configured webhook URL as JSON.

        The ``channel`` is included in the JSON body sent to the webhook.

        Args:
            channel: The channel name, included in the POSTed JSON.
            payload: JSON-serialisable dictionary to send.

        Raises:
            RuntimeError: If the HTTP request fails or returns a non-2xx status code.
        """
        json_body = {"channel": channel, "payload": payload}
        try:
            resp = self._client.post(str(self.url), json=json_body)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Webhook returned {exc.response.status_code} for {self.url}: {exc.response.text.strip()}"
            ) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Failed to POST to {self.url}: {exc}") from exc

    def __del__(self) -> None:
        if hasattr(self, "_client") and self._client and not self._client.is_closed:
            self._client.close()
