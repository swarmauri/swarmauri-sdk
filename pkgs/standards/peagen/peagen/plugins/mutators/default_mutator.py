from __future__ import annotations

from typing import Dict

from peagen.core._external import call_external_agent


class DefaultMutator:
    """Minimal mutator that forwards prompts to an external agent."""

    def __init__(self, agent_env: Dict[str, str] | None = None) -> None:
        self.agent_env = agent_env or {}

    def mutate(self, prompt: str) -> str:
        return call_external_agent(prompt, self.agent_env)
