from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class Body:
    """Lightweight wrapper for response/request payload bytes."""

    value: bytes | str | None

    def decode(self, encoding: str = "utf-8") -> str:
        """Decode the wrapped payload into text."""
        if self.value is None:
            return ""
        if isinstance(self.value, bytes):
            return self.value.decode(encoding)
        return self.value

    def json(self) -> Any:
        """Parse the wrapped payload as JSON."""
        text = self.decode()
        if not text:
            return None
        return json.loads(text)
