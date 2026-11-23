from __future__ import annotations

import json
from typing import Any

from .AwsEventStreamError import AwsEventStreamError


class AwsEventStreamCodec:
    """Translate Python payloads to and from Bedrock Smithy events."""

    @staticmethod
    def _models():
        try:
            from aws_sdk_bedrock_runtime import models
        except ImportError as exc:  # pragma: no cover - Python < 3.12
            raise RuntimeError(
                "AWS Bedrock bidirectional transport requires Python 3.12 "
                "and aws-sdk-bedrock-runtime"
            ) from exc
        return models

    def encode(self, event: Any) -> Any:
        models = self._models()
        payload = (
            event
            if isinstance(event, bytes)
            else json.dumps(event, separators=(",", ":")).encode("utf-8")
        )
        return models.InvokeModelWithBidirectionalStreamInputChunk(
            models.BidirectionalInputPayloadPart(bytes_=payload)
        )

    def decode(self, event: Any) -> Any:
        if event.__class__.__name__ == (
            "InvokeModelWithBidirectionalStreamOutputChunk"
        ):
            payload = event.value.bytes_ or b""
            return json.loads(payload.decode("utf-8"))

        value = getattr(event, "value", None)
        message = getattr(value, "message", None)
        if message is None:
            message = f"Unexpected AWS event stream event: {event!r}"
        raise AwsEventStreamError(str(message))
