"""Live tool-call interface."""

from abc import ABC
from typing import Any, Mapping


class ILiveToolCall(ABC):
    call_id: str
    tool_name: str
    arguments: Mapping[str, Any]
    result_for: str | None
