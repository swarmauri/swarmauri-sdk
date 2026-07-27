"""Live-session event interface."""

from abc import ABC
from typing import Any, Mapping, Optional


class ILiveEvent(ABC):
    kind: str
    payload: Any
    correlation: Mapping[str, str | None]
