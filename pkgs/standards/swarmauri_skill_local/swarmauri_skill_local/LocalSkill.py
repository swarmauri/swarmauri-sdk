from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Literal, Optional

from pydantic import ConfigDict

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_skill_filesystem import FileSystemSkill


@ComponentBase.register_type(FileSystemSkill, "LocalSkill")
class LocalSkill(FileSystemSkill):
    skill_name: Optional[str] = None
    type: Literal["LocalSkill"] = "LocalSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @classmethod
    def from_name(
        cls, skill_name: str, roots: Iterable[str | Path], **overrides: Any
    ) -> "LocalSkill":
        for root in roots:
            candidate = Path(root).expanduser() / skill_name
            if candidate.is_dir():
                data = FileSystemSkill.from_path(candidate, **overrides).model_dump()
                data["skill_name"] = skill_name
                data["type"] = "LocalSkill"
                return cls(**data)
        searched = ", ".join(str(Path(root).expanduser()) for root in roots)
        raise FileNotFoundError(f"Skill '{skill_name}' was not found in: {searched}")
