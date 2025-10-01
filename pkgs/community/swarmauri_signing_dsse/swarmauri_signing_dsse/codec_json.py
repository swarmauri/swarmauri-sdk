"""JSON codec helpers for DSSE envelopes."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .types import DSSEEnvelope


class DSSEJsonCodec:
    """Encode and decode DSSE envelopes using the standard JSON format."""

    def encode(self, envelope: DSSEEnvelope) -> bytes:
        """Serialize a DSSE envelope into canonical JSON bytes."""

        payload = envelope.to_mapping()
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )

    def decode(
        self, blob: bytes | bytearray | str | Mapping[str, Any] | DSSEEnvelope
    ) -> DSSEEnvelope:
        """Deserialize JSON bytes or mappings into a :class:`DSSEEnvelope`."""

        if isinstance(blob, DSSEEnvelope):
            return blob
        if isinstance(blob, Mapping):
            return DSSEEnvelope.from_mapping(dict(blob))
        if isinstance(blob, (bytes, bytearray)):
            data = json.loads(blob)
        elif isinstance(blob, str):
            data = json.loads(blob)
        else:
            raise TypeError("Unsupported DSSE envelope representation for decoding")
        if not isinstance(data, Mapping):
            raise TypeError("Decoded DSSE envelope must produce a mapping")
        return DSSEEnvelope.from_mapping(data)
