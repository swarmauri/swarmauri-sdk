from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from peagen.core._external import call_external_agent
from swarmauri_standard.programs.Program import Program


class LlmProgRewrite:
    """Mutator that rewrites code using a language model."""

    def __init__(self, agent_env: Dict[str, str] | None = None) -> None:
        self.agent_env = agent_env or {}

    def _parent_src(self, program: Program) -> str:
        return "\n".join(program.get_source_files().values())

    def mutate(
        self,
        prompt: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        parent_program: Optional[Program] = None,
        candidates: Optional[Iterable[str]] = None,
    ) -> str:
        ctx = dict(context or {})
        if parent_program is not None:
            ctx.setdefault("parent", self._parent_src(parent_program))
        if candidates is not None:
            ctx.setdefault("candidates", "\n".join(candidates))
        try:
            rendered = prompt.format(**ctx)
        except Exception:
            rendered = prompt
        return call_external_agent(rendered, self.agent_env)
