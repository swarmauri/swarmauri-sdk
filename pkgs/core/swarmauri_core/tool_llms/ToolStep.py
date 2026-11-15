from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProposedToolCall:
    """A call correlated by the runner ID and, when available, provider ID."""

    call_id: str
    name: str
    arguments: dict[str, Any] | str
    provider_call_id: str | None = None


@dataclass(frozen=True)
class ToolStep:
    """A model response and the original items needed to continue."""

    items: list[dict[str, Any]]
    calls: list[ProposedToolCall] = field(default_factory=list)
    content: str | None = None


@dataclass(frozen=True)
class ToolStepResult:
    """The settled value for one call, including a possible denial."""

    call: ProposedToolCall
    value: Any
