from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List

from pydantic import BaseModel, ConfigDict

from swarmauri_base.skills.FileSystemSkillMixin import FileSystemSkillMixin
from swarmauri_base.skills.SkillMetadata import SkillMetadata


class LocalSkillMixin(BaseModel):
    """Resolve skills from deterministic local skill roots."""

    skill_name: str | None = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @classmethod
    def discover(
        cls, roots: Iterable[str | Path] | str | Path
    ) -> List[SkillMetadata]:
        expanded_roots = cls._roots(roots)
        discovered: List[SkillMetadata] = []
        locations: dict[str, str] = {}
        for root in expanded_roots:
            if (root / "SKILL.md").is_file():
                return FileSystemSkillMixin.discover(root)
            if not root.is_dir():
                continue
            for candidate in sorted(root.iterdir()):
                if (
                    not candidate.is_dir()
                    or not (candidate / "SKILL.md").is_file()
                ):
                    continue
                records = FileSystemSkillMixin.discover(candidate)
                for record in records:
                    if record.name in locations:
                        raise ValueError(
                            "Duplicate skill name "
                            f"'{record.name}' at {locations[record.name]} and "
                            f"{record.location}"
                        )
                    locations[record.name] = record.location
                    discovered.append(record)
        return discovered

    @classmethod
    def from_name(
        cls,
        skill_name: str,
        roots: Iterable[str | Path] | str | Path,
        **overrides: Any,
    ):
        for root in cls._roots(roots):
            candidate = root / skill_name
            if candidate.is_dir() and (candidate / "SKILL.md").is_file():
                skill = cls.load(candidate, skill_name=skill_name, **overrides)
                skill.skill_name = skill_name
                return skill
        searched = ", ".join(str(root) for root in cls._roots(roots))
        raise FileNotFoundError(
            f"Skill '{skill_name}' was not found in: {searched}"
        )

    @staticmethod
    def _roots(roots: Iterable[str | Path] | str | Path) -> List[Path]:
        if isinstance(roots, (str, Path)):
            roots = [roots]
        return [Path(root).expanduser().resolve() for root in roots]
