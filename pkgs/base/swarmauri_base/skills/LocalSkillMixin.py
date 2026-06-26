from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict


class LocalSkillMixin(BaseModel):
    skill_name: str | None = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @classmethod
    def from_name(
        cls, skill_name: str, roots: Iterable[str | Path], **overrides: Any
    ):
        expanded_roots = [Path(root).expanduser() for root in roots]
        for root in expanded_roots:
            candidate = root / skill_name
            if candidate.is_dir():
                skill = cls.from_path(candidate, **overrides)
                data = skill.model_dump()
                data["skill_name"] = skill_name
                return cls(**data)
        searched = ", ".join(str(root) for root in expanded_roots)
        raise FileNotFoundError(
            f"Skill '{skill_name}' was not found in: {searched}"
        )
