"""HTTP webhook publisher implementation."""

from __future__ import annotations

from typing import Any, Dict

import httpx


class WebhookPublisher:
    """Send JSON events to an HTTP endpoint."""

    def __init__(self, url: str) -> None:
        """Store the webhook *url*."""
        self._url = url

    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """POST ``payload`` to the webhook as JSON.

        Args:
            channel: Unused channel name, kept for interface compatibility.
            payload: JSON-serialisable dictionary to send.

        Raises:
            RuntimeError: If the request fails or returns non-200.
        """
        try:
            resp = httpx.post(self._url, json={"channel": channel, "payload": payload})
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Failed to POST to {self._url}: {exc}") from exc

        if resp.status_code != 200:
            raise RuntimeError(
                f"Webhook returned {resp.status_code}: {resp.text.strip()}"
            )
