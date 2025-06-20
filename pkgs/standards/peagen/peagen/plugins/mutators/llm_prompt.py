from __future__ import annotations

from typing import Dict

from peagen.core._external import call_external_agent
from swarmauri_standard.programs.Program import Program


class LlmRewrite:
    """Mutator that rewrites code using a language model."""

    def __init__(self, agent_env: Dict[str, str] | None = None) -> None:
        self.agent_env = agent_env or {}

    def _parent_src(self, program: Program) -> str:
        return "\n".join(program.get_source_files().values())

    def mutate(self, prompt: str) -> str:
        return call_external_agent(prompt, self.agent_env)
