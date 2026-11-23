"""Live-session input interface."""

from abc import ABC
from typing import Any


class ILiveInput(ABC):
    kind: str
    payload: Any
    mime_type: str | None
    correlation_id: str | None
