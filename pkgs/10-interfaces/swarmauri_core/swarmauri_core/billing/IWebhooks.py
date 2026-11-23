"""Webhook interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Mapping

from .protos import WebhookEventProto


class IWebhooks(ABC):
    """Operations for webhook processing."""

    @abstractmethod
    def parse_event(
        self, raw_body: bytes, headers: Mapping[str, str]
    ) -> WebhookEventProto:
        """Parse a webhook event."""
