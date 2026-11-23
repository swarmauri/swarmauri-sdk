from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from swarmauri_core.tools.ITool import ITool

from .ToolStep import ToolStep, ToolStepResult


class IToolStepModel(ABC):
    """Opt-in proposal and continuation interface for externally run tools."""

    tool_step_protocol: str

    @abstractmethod
    def initial_tool_history(self, prompt: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def propose_step(
        self, history: Sequence[dict[str, Any]], tools: Mapping[str, ITool]
    ) -> ToolStep:
        pass

    @abstractmethod
    def format_tool_results(
        self, results: Sequence[ToolStepResult]
    ) -> list[dict[str, Any]]:
        pass
