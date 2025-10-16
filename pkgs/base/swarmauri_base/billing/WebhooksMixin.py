"""Mixin for webhook event parsing."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Mapping, cast

from pydantic import BaseModel, ConfigDict

from swarmauri_core.billing import IWebhooks
from swarmauri_core.billing.protos import WebhookEventProto

from .utils import extract_raw_payload
from .refs import WebhookEventRef


class WebhooksMixin(BaseModel, IWebhooks):
    """Delegates webhook parsing to the provider implementation."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto:
        result = self._parse_event(raw_body, headers)
        if isinstance(result, WebhookEventProto):
            return result
        raw = cast(Mapping[str, Any], result)
        payload = extract_raw_payload(raw)
        return WebhookEventRef(
            event_id=str(raw.get("event_id", "")),
            provider=str(raw.get("provider", "")),
            type=str(
                raw.get("type", getattr(payload, "get", lambda *_: "")("type", ""))
            ),
            raw=payload,
        )

    @abstractmethod
    def _parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto | Mapping[str, Any]:
        """Parse the incoming webhook payload."""


__all__ = ["WebhooksMixin"]
