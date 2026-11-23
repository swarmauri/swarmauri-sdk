"""Live-session configuration interface."""

from abc import ABC
from typing import Any, Mapping, Sequence


class ILiveConfig(ABC):
    requested_modalities: Sequence[str]
    tools: Sequence[Any]
    initial_history: Sequence[Any]
    provider_options: Mapping[str, Any]
