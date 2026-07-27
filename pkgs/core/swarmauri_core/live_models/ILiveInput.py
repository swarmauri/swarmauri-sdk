"""Live-session input interface."""

from abc import ABC
from typing import Any, Optional


class ILiveInput(ABC):
    kind: str
    payload: Any
    mime_type: Optional[str]
    correlation_id: Optional[str]
