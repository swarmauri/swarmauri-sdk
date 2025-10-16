"""Mixin for webhook event parsing."""

from __future__ import annotations

from typing import Any, Mapping, cast

from swarmauri_core.billing import IWebhooks, Operation
from swarmauri_core.billing.protos import WebhookEventProto

from .OperationDispatcherMixin import OperationDispatcherMixin, extract_raw_payload
from .refs import WebhookEventRef


class WebhooksMixin(OperationDispatcherMixin, IWebhooks):
    """Delegates webhook parsing to the provider implementation."""

    def parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto:
        result = self._op(
            Operation.PARSE_EVENT,
            {"raw_body": raw_body, "headers": headers},
        )
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


__all__ = ["WebhooksMixin"]
